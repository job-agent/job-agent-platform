"""Tests for extract_must_have_skills node."""

from unittest.mock import patch, MagicMock


from .node import extract_must_have_skills_node
from .schemas import SkillsExtraction


def _create_mock_model(skills: list[str]) -> MagicMock:
    """Create a mock model that returns a SkillsExtraction with the given skills."""
    mock_model = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = SkillsExtraction(skills=skills)
    mock_model.with_structured_output.return_value = mock_structured
    return mock_model


class TestExtractMustHaveSkillsNode:
    """Tests for extract_must_have_skills_node function."""

    def test_returns_empty_list_when_no_description(self):
        """Node returns empty skills list when job has no description."""
        state = {
            "job": {"job_id": 1, "title": "Developer"},
            "status": "started",
            "cv_context": "Python developer",
        }

        result = extract_must_have_skills_node(state)

        assert result["extracted_must_have_skills"] == []

    def test_returns_empty_list_when_description_empty(self):
        """Node returns empty skills list when job description is empty string."""
        state = {
            "job": {"job_id": 1, "title": "Developer", "description": ""},
            "status": "started",
            "cv_context": "Python developer",
        }

        result = extract_must_have_skills_node(state)

        assert result["extracted_must_have_skills"] == []

    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_must_have_skills.node.get_model"
    )
    def test_returns_empty_list_on_model_exception(self, mock_get_model):
        """Node returns empty skills list when model raises exception."""
        mock_get_model.side_effect = Exception("Model unavailable")

        state = {
            "job": {"job_id": 1, "title": "Developer", "description": "Python developer needed"},
            "status": "started",
            "cv_context": "Python developer",
        }

        result = extract_must_have_skills_node(state)

        assert result["extracted_must_have_skills"] == []

    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_must_have_skills.node.get_model"
    )
    def test_extracts_skills_successfully(self, mock_get_model):
        """Node extracts skills from job description using model."""
        expected_skills = ["Python", "Django", "PostgreSQL"]
        mock_get_model.return_value = _create_mock_model(expected_skills)

        state = {
            "job": {
                "job_id": 1,
                "title": "Python Developer",
                "description": "Must have: Python, Django, PostgreSQL",
            },
            "status": "started",
            "cv_context": "Python developer",
        }

        result = extract_must_have_skills_node(state)

        assert result["extracted_must_have_skills"] == expected_skills

    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_must_have_skills.node.get_model"
    )
    def test_handles_result_without_skills_attribute(self, mock_get_model):
        """Node handles model result that lacks skills attribute."""
        mock_model = MagicMock()
        mock_structured = MagicMock()
        mock_result = MagicMock(spec=[])  # Object with no attributes
        mock_structured.invoke.return_value = mock_result
        mock_model.with_structured_output.return_value = mock_structured
        mock_get_model.return_value = mock_model

        state = {
            "job": {
                "job_id": 1,
                "title": "Developer",
                "description": "Some job description",
            },
            "status": "started",
            "cv_context": "Python developer",
        }

        result = extract_must_have_skills_node(state)

        assert result["extracted_must_have_skills"] == []

    @patch(
        "job_agent_backend.workflows.job_processing.nodes.extract_must_have_skills.node.get_model"
    )
    def test_handles_result_with_none_skills(self, mock_get_model):
        """Node handles model result where skills is None."""
        mock_model = MagicMock()
        mock_structured = MagicMock()
        mock_result = MagicMock()
        mock_result.skills = None
        mock_structured.invoke.return_value = mock_result
        mock_model.with_structured_output.return_value = mock_structured
        mock_get_model.return_value = mock_model

        state = {
            "job": {
                "job_id": 1,
                "title": "Developer",
                "description": "Some job description",
            },
            "status": "started",
            "cv_context": "Python developer",
        }

        result = extract_must_have_skills_node(state)

        assert result["extracted_must_have_skills"] == []
