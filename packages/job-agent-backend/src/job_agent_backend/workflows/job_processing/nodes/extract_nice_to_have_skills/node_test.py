"""Tests for extract_nice_to_have_skills node."""

from unittest.mock import MagicMock

from .node import create_extract_nice_to_have_skills_node
from ..extract_must_have_skills.schemas import SkillsExtraction


def _create_mock_model(skills: list[str]) -> MagicMock:
    """Create a mock model that returns a SkillsExtraction with the given skills."""
    mock_model = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = SkillsExtraction(skills=skills)
    mock_model.with_structured_output.return_value = mock_structured
    return mock_model


def _create_mock_factory(mock_model: MagicMock) -> MagicMock:
    """Create a mock model factory that returns the given model."""
    mock_factory = MagicMock()
    mock_factory.get_model.return_value = mock_model
    return mock_factory


class TestExtractNiceToHaveSkillsNode:
    """Tests for extract_nice_to_have_skills_node function."""

    def test_returns_empty_list_when_no_description(self):
        """Node returns empty skills list when job has no description."""
        mock_factory = MagicMock()
        node = create_extract_nice_to_have_skills_node(mock_factory)

        state = {
            "job": {"job_id": 1, "title": "Developer"},
            "status": "started",
            "cv_context": "Python developer",
        }

        result = node(state)

        assert result["extracted_nice_to_have_skills"] == []

    def test_returns_empty_list_when_description_empty(self):
        """Node returns empty skills list when job description is empty string."""
        mock_factory = MagicMock()
        node = create_extract_nice_to_have_skills_node(mock_factory)

        state = {
            "job": {"job_id": 1, "title": "Developer", "description": ""},
            "status": "started",
            "cv_context": "Python developer",
        }

        result = node(state)

        assert result["extracted_nice_to_have_skills"] == []

    def test_returns_empty_list_on_model_exception(self):
        """Node returns empty skills list when model raises exception."""
        mock_factory = MagicMock()
        mock_factory.get_model.side_effect = Exception("Model unavailable")
        node = create_extract_nice_to_have_skills_node(mock_factory)

        state = {
            "job": {"job_id": 1, "title": "Developer", "description": "Python developer needed"},
            "status": "started",
            "cv_context": "Python developer",
        }

        result = node(state)

        assert result["extracted_nice_to_have_skills"] == []

    def test_extracts_skills_successfully(self):
        """Node extracts nice-to-have skills from job description using model."""
        expected_skills = ["Docker", "Kubernetes", "AWS"]
        mock_model = _create_mock_model(expected_skills)
        mock_factory = _create_mock_factory(mock_model)
        node = create_extract_nice_to_have_skills_node(mock_factory)

        state = {
            "job": {
                "job_id": 1,
                "title": "Python Developer",
                "description": "Nice to have: Docker, Kubernetes, AWS",
            },
            "status": "started",
            "cv_context": "Python developer",
        }

        result = node(state)

        assert result["extracted_nice_to_have_skills"] == expected_skills

    def test_handles_result_without_skills_attribute(self):
        """Node handles model result that lacks skills attribute."""
        mock_model = MagicMock()
        mock_structured = MagicMock()
        mock_result = MagicMock(spec=[])  # Object with no attributes
        mock_structured.invoke.return_value = mock_result
        mock_model.with_structured_output.return_value = mock_structured
        mock_factory = _create_mock_factory(mock_model)
        node = create_extract_nice_to_have_skills_node(mock_factory)

        state = {
            "job": {
                "job_id": 1,
                "title": "Developer",
                "description": "Some job description",
            },
            "status": "started",
            "cv_context": "Python developer",
        }

        result = node(state)

        assert result["extracted_nice_to_have_skills"] == []

    def test_handles_result_with_none_skills(self):
        """Node handles model result where skills is None."""
        mock_model = MagicMock()
        mock_structured = MagicMock()
        mock_result = MagicMock()
        mock_result.skills = None
        mock_structured.invoke.return_value = mock_result
        mock_model.with_structured_output.return_value = mock_structured
        mock_factory = _create_mock_factory(mock_model)
        node = create_extract_nice_to_have_skills_node(mock_factory)

        state = {
            "job": {
                "job_id": 1,
                "title": "Developer",
                "description": "Some job description",
            },
            "status": "started",
            "cv_context": "Python developer",
        }

        result = node(state)

        assert result["extracted_nice_to_have_skills"] == []
