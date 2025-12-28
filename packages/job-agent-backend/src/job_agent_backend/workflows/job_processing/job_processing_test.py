"""Tests for job processing workflow."""

from unittest.mock import MagicMock
import pytest

from job_agent_backend.workflows import run_job_processing
from job_agent_backend.workflows.job_processing.nodes.extract_must_have_skills.schemas import (
    SkillsExtraction,
)


def create_mock_model(result_obj):
    """Helper to create a mock model with structured output."""
    mock_model = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = result_obj
    mock_model.with_structured_output.return_value = mock_structured
    return mock_model


def create_mock_model_factory(
    embedding_model=None,
    must_have_model=None,
    nice_to_have_model=None,
):
    """Create a mock model factory that returns different models based on call params."""
    mock_factory = MagicMock()

    def get_model_side_effect(**kwargs):
        model_name = kwargs.get("model_name", "")
        model_id = kwargs.get("model_id", "")

        # Embedding model for relevance check
        if "sentence-transformers" in model_name or kwargs.get("task") == "embedding":
            return embedding_model

        # Skills extraction models (identified by model_id containing "phi3")
        if "phi3" in model_id or "phi3" in model_name:
            # Return both models alternately for must-have and nice-to-have
            if must_have_model is not None:
                return must_have_model

        return MagicMock()

    mock_factory.get_model.side_effect = get_model_side_effect
    return mock_factory


class TestJobProcessingWorkflow:
    """Test suite for job processing workflow."""

    def test_relevant_job_extracts_skills(
        self,
        sample_job_dict,
        sample_cv_content,
        job_repository_factory_stub,
        mock_embedding_model_factory,
    ):
        """Test that relevant job goes through complete skill extraction."""
        # Mock embedding model for relevance check (similarity >= 0.4 = relevant)
        embedding_model = mock_embedding_model_factory(similarity_score=0.8)

        mock_must_result = MagicMock()
        mock_must_result.skills = ["Python", "Django", "PostgreSQL"]

        mock_nice_result = MagicMock()
        mock_nice_result.skills = ["Docker", "Kubernetes"]

        # Create a model factory that returns appropriate models
        mock_factory = MagicMock()
        call_count = {"value": 0}

        def get_model_side_effect(**kwargs):
            if kwargs.get("model_id") == "embedding":
                return embedding_model
            # For skill extraction, alternate between must-have and nice-to-have
            call_count["value"] += 1
            if call_count["value"] == 1:
                return create_mock_model(mock_must_result)
            else:
                return create_mock_model(mock_nice_result)

        mock_factory.get_model.side_effect = get_model_side_effect

        result = run_job_processing(
            sample_job_dict,
            sample_cv_content,
            job_repository_factory=job_repository_factory_stub,
            model_factory=mock_factory,
        )

        assert result["is_relevant"] is True
        assert "extracted_must_have_skills" in result
        assert "extracted_nice_to_have_skills" in result
        assert result["status"] == "completed"

    def test_irrelevant_job_skips_skill_extraction(
        self,
        sample_irrelevant_job_dict,
        sample_cv_content,
        job_repository_factory_stub,
        mock_embedding_model_factory,
    ):
        """Test that irrelevant job skips skill extraction."""
        # Mock embedding model for relevance check (similarity < 0.4 = irrelevant)
        embedding_model = mock_embedding_model_factory(similarity_score=0.3)

        mock_factory = MagicMock()
        mock_factory.get_model.return_value = embedding_model

        result = run_job_processing(
            sample_irrelevant_job_dict,
            sample_cv_content,
            job_repository_factory=job_repository_factory_stub,
            model_factory=mock_factory,
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

    def test_irrelevant_job_is_stored_with_is_relevant_false(
        self,
        sample_irrelevant_job_dict,
        sample_cv_content,
        mock_embedding_model_factory,
    ):
        """Test that irrelevant jobs are stored with is_relevant=False."""
        # Mock embedding model for relevance check (similarity < 0.4 = irrelevant)
        embedding_model = mock_embedding_model_factory(similarity_score=0.3)

        mock_factory = MagicMock()
        mock_factory.get_model.return_value = embedding_model

        mock_repository = MagicMock()
        mock_repository.create.return_value = MagicMock(id=42)
        factory = MagicMock(return_value=mock_repository)

        result = run_job_processing(
            sample_irrelevant_job_dict,
            sample_cv_content,
            job_repository_factory=factory,
            model_factory=mock_factory,
        )

        assert result["status"] in ["started", "completed"]
        assert result["is_relevant"] is False
        # Irrelevant jobs are now stored (with is_relevant=False)
        factory.assert_called_once()
        mock_repository.create.assert_called_once()
        created_job = mock_repository.create.call_args[0][0]
        assert created_job["is_relevant"] is False
        # Irrelevant jobs skip skill extraction
        assert "must_have_skills" not in created_job
        assert "nice_to_have_skills" not in created_job

    def test_workflow_state_includes_job_data(
        self,
        sample_job_dict,
        sample_cv_content,
        job_repository_factory_stub,
        mock_embedding_model_factory,
    ):
        """Test that final state includes original job data."""
        # Mock embedding model for relevance check (similarity >= 0.4 = relevant)
        embedding_model = mock_embedding_model_factory(similarity_score=0.8)

        mock_must_result = MagicMock()
        mock_must_result.skills = ["Python"]

        mock_nice_result = MagicMock()
        mock_nice_result.skills = []

        mock_factory = MagicMock()
        call_count = {"value": 0}

        def get_model_side_effect(**kwargs):
            if kwargs.get("model_id") == "embedding":
                return embedding_model
            call_count["value"] += 1
            if call_count["value"] == 1:
                return create_mock_model(mock_must_result)
            else:
                return create_mock_model(mock_nice_result)

        mock_factory.get_model.side_effect = get_model_side_effect

        result = run_job_processing(
            sample_job_dict,
            sample_cv_content,
            job_repository_factory=job_repository_factory_stub,
            model_factory=mock_factory,
        )

        assert result["job"] == sample_job_dict
        assert result["cv_context"] == sample_cv_content

    def test_workflow_with_empty_skills_extracts(
        self,
        sample_job_dict,
        sample_cv_content,
        job_repository_factory_stub,
        mock_embedding_model_factory,
    ):
        """Test workflow handles empty skills extraction gracefully."""
        # Mock embedding model for relevance check (similarity >= 0.4 = relevant)
        embedding_model = mock_embedding_model_factory(similarity_score=0.8)

        mock_empty_result = MagicMock()
        mock_empty_result.skills = []

        mock_factory = MagicMock()

        def get_model_side_effect(**kwargs):
            if kwargs.get("model_id") == "embedding":
                return embedding_model
            return create_mock_model(mock_empty_result)

        mock_factory.get_model.side_effect = get_model_side_effect

        result = run_job_processing(
            sample_job_dict,
            sample_cv_content,
            job_repository_factory=job_repository_factory_stub,
            model_factory=mock_factory,
        )

        assert result["is_relevant"] is True
        assert result["extracted_must_have_skills"] == []
        assert result["extracted_nice_to_have_skills"] == []
        assert result["status"] == "completed"

    def test_workflow_cv_context_passed_to_all_nodes(
        self,
        sample_job_dict,
        sample_cv_content,
        job_repository_factory_stub,
        mock_embedding_model_factory,
    ):
        """Test that CV context is passed to all workflow nodes."""
        # Mock embedding model for relevance check (similarity >= 0.4 = relevant)
        embedding_model = mock_embedding_model_factory(similarity_score=0.8)

        mock_result = SkillsExtraction(skills=["Python"])

        mock_factory = MagicMock()

        def get_model_side_effect(**kwargs):
            if kwargs.get("model_id") == "embedding":
                return embedding_model
            return create_mock_model(mock_result)

        mock_factory.get_model.side_effect = get_model_side_effect

        result = run_job_processing(
            sample_job_dict,
            sample_cv_content,
            job_repository_factory=job_repository_factory_stub,
            model_factory=mock_factory,
        )

        assert result["cv_context"] == sample_cv_content

    def test_workflow_handles_job_without_salary(
        self,
        sample_cv_content,
        job_repository_factory_stub,
        mock_embedding_model_factory,
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
        embedding_model = mock_embedding_model_factory(similarity_score=0.8)

        mock_result = SkillsExtraction(skills=["Python"])

        mock_factory = MagicMock()

        def get_model_side_effect(**kwargs):
            if kwargs.get("model_id") == "embedding":
                return embedding_model
            return create_mock_model(mock_result)

        mock_factory.get_model.side_effect = get_model_side_effect

        result = run_job_processing(
            job_without_salary,
            sample_cv_content,
            job_repository_factory=job_repository_factory_stub,
            model_factory=mock_factory,
        )

        assert result["status"] == "completed"
        assert result["is_relevant"] is True

    def test_workflow_returns_final_state_structure(
        self,
        sample_job_dict,
        sample_cv_content,
        job_repository_factory_stub,
        mock_embedding_model_factory,
    ):
        """Test that workflow returns expected state structure."""
        # Mock embedding model for relevance check (similarity < 0.4 = irrelevant)
        embedding_model = mock_embedding_model_factory(similarity_score=0.3)

        mock_factory = MagicMock()
        mock_factory.get_model.return_value = embedding_model

        result = run_job_processing(
            sample_job_dict,
            sample_cv_content,
            job_repository_factory=job_repository_factory_stub,
            model_factory=mock_factory,
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

    def test_relevant_job_stores_to_repository(
        self,
        sample_job_dict,
        sample_cv_content,
        mock_embedding_model_factory,
    ):
        """Test that relevant jobs are stored to the repository with extracted skills."""
        embedding_model = mock_embedding_model_factory(similarity_score=0.8)

        # Both skill extraction nodes use the same model_id and run in parallel,
        # so we use the same mock result for both to avoid race conditions
        mock_skill_result = SkillsExtraction(skills=["Python", "Django"])

        mock_factory = MagicMock()

        def get_model_side_effect(**kwargs):
            if kwargs.get("model_id") == "embedding":
                return embedding_model
            # Return new mock for each call to simulate independent model instances
            return create_mock_model(mock_skill_result)

        mock_factory.get_model.side_effect = get_model_side_effect

        mock_repository = MagicMock()
        mock_repository.create.return_value = MagicMock(id=42)
        job_repository_factory = MagicMock(return_value=mock_repository)

        result = run_job_processing(
            sample_job_dict,
            sample_cv_content,
            job_repository_factory=job_repository_factory,
            model_factory=mock_factory,
        )

        job_repository_factory.assert_called_once()
        mock_repository.create.assert_called_once()
        created_job = mock_repository.create.call_args[0][0]
        # Both skill extraction nodes use same model_id, so they extract same skills
        assert created_job["must_have_skills"] == ["Python", "Django"]
        assert created_job["nice_to_have_skills"] == ["Python", "Django"]
        assert result["status"] == "completed"

    def test_workflow_continues_after_store_job_error(
        self,
        sample_job_dict,
        sample_cv_content,
        mock_embedding_model_factory,
    ):
        """Test that workflow completes even when repository raises exception."""
        embedding_model = mock_embedding_model_factory(similarity_score=0.8)

        mock_result = SkillsExtraction(skills=["Python"])

        mock_factory = MagicMock()

        def get_model_side_effect(**kwargs):
            if kwargs.get("model_id") == "embedding":
                return embedding_model
            return create_mock_model(mock_result)

        mock_factory.get_model.side_effect = get_model_side_effect

        mock_repository = MagicMock()
        mock_repository.create.side_effect = Exception("Database error")
        job_repository_factory = MagicMock(return_value=mock_repository)

        result = run_job_processing(
            sample_job_dict,
            sample_cv_content,
            job_repository_factory=job_repository_factory,
            model_factory=mock_factory,
        )

        # Workflow continues to completion despite store error
        mock_repository.create.assert_called_once()
        assert result["status"] == "completed"
        assert result["is_relevant"] is True
