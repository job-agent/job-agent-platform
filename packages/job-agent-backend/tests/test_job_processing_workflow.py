"""Integration tests for job processing workflow."""

from unittest.mock import patch, MagicMock
import pytest

from job_agent_backend.workflows import run_job_processing
from jobs_repository.models import Job
from jobs_repository.repository.job_repository import JobRepository


@pytest.fixture
def job_repository_factory_stub():
    """Provide a stub job repository factory."""

    def factory():
        repository = MagicMock()
        repository.create.return_value = MagicMock(id=1)
        return repository

    return factory


@pytest.fixture
def job_repository_factory_with_session(db_session):
    """Provide a job repository factory that reuses the test session."""

    def factory():
        return JobRepository(session=db_session)

    return factory


def create_mock_chat_openai(result_obj):
    """Helper to create a mock ChatOpenAI with structured output."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = result_obj
    mock_llm.with_structured_output.return_value = mock_structured
    return mock_llm


class TestJobProcessingWorkflow:
    """Test suite for job processing workflow."""

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.ChatOpenAI")
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_must_have_skills.node.ChatOpenAI"
    )
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_nice_to_have_skills.node.ChatOpenAI"
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

        mock_relevance_result = MagicMock()
        mock_relevance_result.is_relevant = True
        mock_relevance_chat.return_value = create_mock_chat_openai(mock_relevance_result)

        mock_must_result = MagicMock()
        mock_must_result.skills = ["Python", "Django", "PostgreSQL"]
        mock_must_chat.return_value = create_mock_chat_openai(mock_must_result)

        mock_nice_result = MagicMock()
        mock_nice_result.skills = ["Docker", "Kubernetes"]
        mock_nice_chat.return_value = create_mock_chat_openai(mock_nice_result)

        result = run_job_processing(
            sample_job_dict,
            sample_cv_content,
            job_repository_factory=job_repository_factory_stub,
        )

        assert result["is_relevant"] is True
        assert "extracted_must_have_skills" in result
        assert "extracted_nice_to_have_skills" in result
        assert result["status"] == "completed"

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.ChatOpenAI")
    def test_irrelevant_job_skips_skill_extraction(
        self,
        mock_relevance_chat,
        sample_irrelevant_job_dict,
        sample_cv_content,
        job_repository_factory_stub,
    ):
        """Test that irrelevant job skips skill extraction."""

        mock_relevance_result = MagicMock()
        mock_relevance_result.is_relevant = False
        mock_relevance_chat.return_value = create_mock_chat_openai(mock_relevance_result)

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

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.ChatOpenAI")
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_must_have_skills.node.ChatOpenAI"
    )
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_nice_to_have_skills.node.ChatOpenAI"
    )
    def test_workflow_with_database_session_stores_job(
        self,
        mock_nice_chat,
        mock_must_chat,
        mock_relevance_chat,
        sample_job_dict,
        sample_cv_content,
        db_session,
        job_repository_factory_with_session,
    ):
        """Test that workflow stores job in database when session is provided."""

        mock_relevance_result = MagicMock()
        mock_relevance_result.is_relevant = True
        mock_relevance_chat.return_value = create_mock_chat_openai(mock_relevance_result)

        mock_must_result = MagicMock()
        mock_must_result.skills = ["Python"]
        mock_must_chat.return_value = create_mock_chat_openai(mock_must_result)

        mock_nice_result = MagicMock()
        mock_nice_result.skills = ["Docker"]
        mock_nice_chat.return_value = create_mock_chat_openai(mock_nice_result)

        run_job_processing(
            sample_job_dict,
            sample_cv_content,
            job_repository_factory=job_repository_factory_with_session,
        )

        stored_job = (
            db_session.query(Job).filter_by(external_id=str(sample_job_dict["job_id"])).first()
        )
        assert stored_job is not None
        assert stored_job.title == sample_job_dict["title"]
        assert len(stored_job.must_have_skills) > 0

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.ChatOpenAI")
    def test_workflow_without_database_session_completes(
        self,
        mock_relevance_chat,
        sample_irrelevant_job_dict,
        sample_cv_content,
    ):
        """Test that workflow completes without database session."""
        mock_relevance_result = MagicMock()
        mock_relevance_result.is_relevant = False
        mock_relevance_chat.return_value = create_mock_chat_openai(mock_relevance_result)

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

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.ChatOpenAI")
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_must_have_skills.node.ChatOpenAI"
    )
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_nice_to_have_skills.node.ChatOpenAI"
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

        mock_relevance_result = MagicMock()
        mock_relevance_result.is_relevant = True
        mock_relevance_chat.return_value = create_mock_chat_openai(mock_relevance_result)

        mock_must_result = MagicMock()
        mock_must_result.skills = ["Python"]
        mock_must_chat.return_value = create_mock_chat_openai(mock_must_result)

        mock_nice_result = MagicMock()
        mock_nice_result.skills = []
        mock_nice_chat.return_value = create_mock_chat_openai(mock_nice_result)

        result = run_job_processing(
            sample_job_dict,
            sample_cv_content,
            job_repository_factory=job_repository_factory_stub,
        )

        assert result["job"] == sample_job_dict
        assert result["cv_context"] == sample_cv_content

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.ChatOpenAI")
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_must_have_skills.node.ChatOpenAI"
    )
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_nice_to_have_skills.node.ChatOpenAI"
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

        mock_relevance_result = MagicMock()
        mock_relevance_result.is_relevant = True
        mock_relevance_chat.return_value = create_mock_chat_openai(mock_relevance_result)

        mock_must_result = MagicMock()
        mock_must_result.skills = []
        mock_must_chat.return_value = create_mock_chat_openai(mock_must_result)

        mock_nice_result = MagicMock()
        mock_nice_result.skills = []
        mock_nice_chat.return_value = create_mock_chat_openai(mock_nice_result)

        result = run_job_processing(
            sample_job_dict,
            sample_cv_content,
            job_repository_factory=job_repository_factory_stub,
        )

        assert result["is_relevant"] is True
        assert result["extracted_must_have_skills"] == []
        assert result["extracted_nice_to_have_skills"] == []
        assert result["status"] == "completed"

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.ChatOpenAI")
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_must_have_skills.node.ChatOpenAI"
    )
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_nice_to_have_skills.node.ChatOpenAI"
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
        mock_relevance_result = MagicMock()
        mock_relevance_result.is_relevant = True
        mock_relevance_chat.return_value = create_mock_chat_openai(mock_relevance_result)

        mock_must_result = MagicMock()
        mock_must_result.skills = ["Python"]
        mock_must_chat.return_value = create_mock_chat_openai(mock_must_result)

        mock_nice_result = MagicMock()
        mock_nice_result.skills = []
        mock_nice_chat.return_value = create_mock_chat_openai(mock_nice_result)

        result = run_job_processing(
            sample_job_dict,
            sample_cv_content,
            job_repository_factory=job_repository_factory_stub,
        )

        assert result["cv_context"] == sample_cv_content

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.ChatOpenAI")
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_must_have_skills.node.ChatOpenAI"
    )
    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_nice_to_have_skills.node.ChatOpenAI"
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

        mock_relevance_result = MagicMock()
        mock_relevance_result.is_relevant = True
        mock_relevance_chat.return_value = create_mock_chat_openai(mock_relevance_result)

        mock_must_result = MagicMock()
        mock_must_result.skills = ["Python"]
        mock_must_chat.return_value = create_mock_chat_openai(mock_must_result)

        mock_nice_result = MagicMock()
        mock_nice_result.skills = []
        mock_nice_chat.return_value = create_mock_chat_openai(mock_nice_result)

        result = run_job_processing(
            job_without_salary,
            sample_cv_content,
            job_repository_factory=job_repository_factory_stub,
        )

        assert result["status"] == "completed"
        assert result["is_relevant"] is True

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.ChatOpenAI")
    def test_workflow_returns_final_state_structure(
        self,
        mock_relevance_chat,
        sample_job_dict,
        sample_cv_content,
        job_repository_factory_stub,
    ):
        """Test that workflow returns expected state structure."""
        mock_relevance_result = MagicMock()
        mock_relevance_result.is_relevant = False
        mock_relevance_chat.return_value = create_mock_chat_openai(mock_relevance_result)

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
