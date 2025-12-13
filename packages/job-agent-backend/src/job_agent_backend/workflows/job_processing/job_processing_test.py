"""Tests for job processing workflow."""

from unittest.mock import patch, MagicMock
import pytest

from job_agent_backend.workflows import run_job_processing


def create_mock_model(result_obj):
    """Helper to create a mock model with structured output."""
    mock_model = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = result_obj
    mock_model.with_structured_output.return_value = mock_structured
    return mock_model


def create_mock_embedding_model(similarity_score=0.8):
    """
    Helper to create a mock embedding model.

    Args:
        similarity_score: The desired cosine similarity between CV and job embeddings.
                         Values >= 0.4 result in relevant jobs, < 0.4 in irrelevant jobs.

    Returns:
        Mock embedding model with embed_query method that returns valid embeddings.
    """
    import numpy as np

    mock_model = MagicMock()

    # Create two embeddings that will produce the desired similarity score
    # Using simple vectors for predictable cosine similarity
    cv_embedding = np.array([1.0, 0.0, 0.0])
    job_embedding = np.array([similarity_score, np.sqrt(1 - similarity_score**2), 0.0])

    # Normalize to unit vectors for consistent cosine similarity
    cv_embedding = cv_embedding / np.linalg.norm(cv_embedding)
    job_embedding = job_embedding / np.linalg.norm(job_embedding)

    # Set up the mock to return these embeddings
    # First call returns CV embedding, second call returns job embedding
    mock_model.embed_query.side_effect = [cv_embedding.tolist(), job_embedding.tolist()]

    return mock_model


class TestJobProcessingWorkflow:
    """Test suite for job processing workflow."""

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.get_model")
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_must_have_skills.node.get_model"
    )
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_nice_to_have_skills.node.get_model"
    )
    def test_relevant_job_extracts_skills(
        self,
        mock_nice_chat,
        mock_must_chat,
        mock_relevance_chat,
        sample_job_dict,
        sample_cv_content,
        job_repository_factory_stub,
    ):
        """Test that relevant job goes through complete skill extraction."""

        # Mock embedding model for relevance check (similarity >= 0.4 = relevant)
        mock_relevance_chat.return_value = create_mock_embedding_model(similarity_score=0.8)

        mock_must_result = MagicMock()
        mock_must_result.skills = ["Python", "Django", "PostgreSQL"]
        mock_must_chat.return_value = create_mock_model(mock_must_result)

        mock_nice_result = MagicMock()
        mock_nice_result.skills = ["Docker", "Kubernetes"]
        mock_nice_chat.return_value = create_mock_model(mock_nice_result)

        result = run_job_processing(
            sample_job_dict,
            sample_cv_content,
            job_repository_factory=job_repository_factory_stub,
        )

        assert result["is_relevant"] is True
        assert "extracted_must_have_skills" in result
        assert "extracted_nice_to_have_skills" in result
        assert result["status"] == "completed"

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.get_model")
    def test_irrelevant_job_skips_skill_extraction(
        self,
        mock_relevance_chat,
        sample_irrelevant_job_dict,
        sample_cv_content,
        job_repository_factory_stub,
    ):
        """Test that irrelevant job skips skill extraction."""

        # Mock embedding model for relevance check (similarity < 0.4 = irrelevant)
        mock_relevance_chat.return_value = create_mock_embedding_model(similarity_score=0.3)

        result = run_job_processing(
            sample_irrelevant_job_dict,
            sample_cv_content,
            job_repository_factory=job_repository_factory_stub,
        )

        assert result["is_relevant"] is False
        assert "extracted_must_have_skills" not in result
        assert "extracted_nice_to_have_skills" not in result

        assert result["status"] in ["started", "completed"]

    def test_workflow_with_empty_cv_raises_error(
        self,
        sample_job_dict,
        job_repository_factory_stub,
    ):
        """Test that empty CV raises ValueError."""
        with pytest.raises(ValueError, match="CV content is required"):
            run_job_processing(
                sample_job_dict,
                "",
                job_repository_factory=job_repository_factory_stub,
            )

    def test_workflow_with_none_cv_raises_error(
        self,
        sample_job_dict,
        job_repository_factory_stub,
    ):
        """Test that None CV raises ValueError."""
        with pytest.raises(ValueError, match="CV content is required"):
            run_job_processing(
                sample_job_dict,
                None,
                job_repository_factory=job_repository_factory_stub,
            )

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.get_model")
    def test_workflow_without_database_session_completes(
        self,
        mock_relevance_chat,
        sample_irrelevant_job_dict,
        sample_cv_content,
    ):
        """Test that workflow completes without database session."""
        # Mock embedding model for relevance check (similarity < 0.4 = irrelevant)
        mock_relevance_chat.return_value = create_mock_embedding_model(similarity_score=0.3)

        factory = MagicMock()
        factory.return_value = MagicMock()

        result = run_job_processing(
            sample_irrelevant_job_dict,
            sample_cv_content,
            job_repository_factory=factory,
        )

        assert result["status"] in ["started", "completed"]
        assert result["is_relevant"] is False
        factory.assert_not_called()

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.get_model")
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_must_have_skills.node.get_model"
    )
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_nice_to_have_skills.node.get_model"
    )
    def test_workflow_state_includes_job_data(
        self,
        mock_nice_chat,
        mock_must_chat,
        mock_relevance_chat,
        sample_job_dict,
        sample_cv_content,
        job_repository_factory_stub,
    ):
        """Test that final state includes original job data."""

        # Mock embedding model for relevance check (similarity >= 0.4 = relevant)
        mock_relevance_chat.return_value = create_mock_embedding_model(similarity_score=0.8)

        mock_must_result = MagicMock()
        mock_must_result.skills = ["Python"]
        mock_must_chat.return_value = create_mock_model(mock_must_result)

        mock_nice_result = MagicMock()
        mock_nice_result.skills = []
        mock_nice_chat.return_value = create_mock_model(mock_nice_result)

        result = run_job_processing(
            sample_job_dict,
            sample_cv_content,
            job_repository_factory=job_repository_factory_stub,
        )

        assert result["job"] == sample_job_dict
        assert result["cv_context"] == sample_cv_content

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.get_model")
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_must_have_skills.node.get_model"
    )
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_nice_to_have_skills.node.get_model"
    )
    def test_workflow_with_empty_skills_extracts(
        self,
        mock_nice_chat,
        mock_must_chat,
        mock_relevance_chat,
        sample_job_dict,
        sample_cv_content,
        job_repository_factory_stub,
    ):
        """Test workflow handles empty skills extraction gracefully."""

        # Mock embedding model for relevance check (similarity >= 0.4 = relevant)
        mock_relevance_chat.return_value = create_mock_embedding_model(similarity_score=0.8)

        mock_must_result = MagicMock()
        mock_must_result.skills = []
        mock_must_chat.return_value = create_mock_model(mock_must_result)

        mock_nice_result = MagicMock()
        mock_nice_result.skills = []
        mock_nice_chat.return_value = create_mock_model(mock_nice_result)

        result = run_job_processing(
            sample_job_dict,
            sample_cv_content,
            job_repository_factory=job_repository_factory_stub,
        )

        assert result["is_relevant"] is True
        assert result["extracted_must_have_skills"] == []
        assert result["extracted_nice_to_have_skills"] == []
        assert result["status"] == "completed"

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.get_model")
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_must_have_skills.node.get_model"
    )
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_nice_to_have_skills.node.get_model"
    )
    def test_workflow_cv_context_passed_to_all_nodes(
        self,
        mock_nice_chat,
        mock_must_chat,
        mock_relevance_chat,
        sample_job_dict,
        sample_cv_content,
        job_repository_factory_stub,
    ):
        """Test that CV context is passed to all workflow nodes."""
        # Mock embedding model for relevance check (similarity >= 0.4 = relevant)
        mock_relevance_chat.return_value = create_mock_embedding_model(similarity_score=0.8)

        mock_must_result = MagicMock()
        mock_must_result.skills = ["Python"]
        mock_must_chat.return_value = create_mock_model(mock_must_result)

        mock_nice_result = MagicMock()
        mock_nice_result.skills = []
        mock_nice_chat.return_value = create_mock_model(mock_nice_result)

        result = run_job_processing(
            sample_job_dict,
            sample_cv_content,
            job_repository_factory=job_repository_factory_stub,
        )

        assert result["cv_context"] == sample_cv_content

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.get_model")
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_must_have_skills.node.get_model"
    )
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_nice_to_have_skills.node.get_model"
    )
    def test_workflow_handles_job_without_salary(
        self,
        mock_nice_chat,
        mock_must_chat,
        mock_relevance_chat,
        sample_cv_content,
        job_repository_factory_stub,
    ):
        """Test workflow handles job without salary information."""
        job_without_salary = {
            "job_id": 999,
            "title": "Developer",
            "url": "https://example.com/999",
            "description": "Developer position",
            "company": {"name": "TestCo"},
            "category": "Software",
            "date_posted": "2024-01-15T10:00:00Z",
            "employment_type": "FULL_TIME",
            "experience_months": 24.0,
            "location": {"region": "Remote", "is_remote": True},
        }

        # Mock embedding model for relevance check (similarity >= 0.4 = relevant)
        mock_relevance_chat.return_value = create_mock_embedding_model(similarity_score=0.8)

        mock_must_result = MagicMock()
        mock_must_result.skills = ["Python"]
        mock_must_chat.return_value = create_mock_model(mock_must_result)

        mock_nice_result = MagicMock()
        mock_nice_result.skills = []
        mock_nice_chat.return_value = create_mock_model(mock_nice_result)

        result = run_job_processing(
            job_without_salary,
            sample_cv_content,
            job_repository_factory=job_repository_factory_stub,
        )

        assert result["status"] == "completed"
        assert result["is_relevant"] is True

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.get_model")
    def test_workflow_returns_final_state_structure(
        self,
        mock_relevance_chat,
        sample_job_dict,
        sample_cv_content,
        job_repository_factory_stub,
    ):
        """Test that workflow returns expected state structure."""
        # Mock embedding model for relevance check (similarity < 0.4 = irrelevant)
        mock_relevance_chat.return_value = create_mock_embedding_model(similarity_score=0.3)

        result = run_job_processing(
            sample_job_dict,
            sample_cv_content,
            job_repository_factory=job_repository_factory_stub,
        )

        assert "job" in result
        assert "status" in result
        assert "cv_context" in result
        assert "is_relevant" in result
        assert isinstance(result, dict)

    def test_non_callable_repository_factory_raises_error(
        self,
        sample_job_dict,
        sample_cv_content,
    ):
        """Test that non-callable job_repository_factory raises ValueError."""
        with pytest.raises(ValueError, match="job_repository_factory must be callable"):
            run_job_processing(
                sample_job_dict,
                sample_cv_content,
                job_repository_factory="not_callable",
            )

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.get_model")
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_must_have_skills.node.get_model"
    )
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_nice_to_have_skills.node.get_model"
    )
    def test_relevant_job_stores_to_repository(
        self,
        mock_nice_chat,
        mock_must_chat,
        mock_relevance_chat,
        sample_job_dict,
        sample_cv_content,
    ):
        """Test that relevant jobs are stored to the repository with extracted skills."""
        mock_relevance_chat.return_value = create_mock_embedding_model(similarity_score=0.8)

        mock_must_result = MagicMock()
        mock_must_result.skills = ["Python", "Django"]
        mock_must_chat.return_value = create_mock_model(mock_must_result)

        mock_nice_result = MagicMock()
        mock_nice_result.skills = ["Docker"]
        mock_nice_chat.return_value = create_mock_model(mock_nice_result)

        mock_repository = MagicMock()
        mock_repository.create.return_value = MagicMock(id=42)
        job_repository_factory = MagicMock(return_value=mock_repository)

        result = run_job_processing(
            sample_job_dict,
            sample_cv_content,
            job_repository_factory=job_repository_factory,
        )

        job_repository_factory.assert_called_once()
        mock_repository.create.assert_called_once()
        created_job = mock_repository.create.call_args[0][0]
        assert created_job["must_have_skills"] == ["Python", "Django"]
        assert created_job["nice_to_have_skills"] == ["Docker"]
        assert result["status"] == "completed"

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.get_model")
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_must_have_skills.node.get_model"
    )
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_nice_to_have_skills.node.get_model"
    )
    def test_workflow_continues_after_store_job_error(
        self,
        mock_nice_chat,
        mock_must_chat,
        mock_relevance_chat,
        sample_job_dict,
        sample_cv_content,
    ):
        """Test that workflow completes even when repository raises exception."""
        mock_relevance_chat.return_value = create_mock_embedding_model(similarity_score=0.8)

        mock_must_result = MagicMock()
        mock_must_result.skills = ["Python"]
        mock_must_chat.return_value = create_mock_model(mock_must_result)

        mock_nice_result = MagicMock()
        mock_nice_result.skills = []
        mock_nice_chat.return_value = create_mock_model(mock_nice_result)

        mock_repository = MagicMock()
        mock_repository.create.side_effect = Exception("Database error")
        job_repository_factory = MagicMock(return_value=mock_repository)

        result = run_job_processing(
            sample_job_dict,
            sample_cv_content,
            job_repository_factory=job_repository_factory,
        )

        # Workflow continues to completion despite store error
        mock_repository.create.assert_called_once()
        assert result["status"] == "completed"
        assert result["is_relevant"] is True
