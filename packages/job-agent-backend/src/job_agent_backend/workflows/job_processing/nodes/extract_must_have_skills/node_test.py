"""Tests for extract_must_have_skills node."""

from unittest.mock import MagicMock

from .node import create_extract_must_have_skills_node
from .schemas import SkillsExtraction


def _create_mock_model(skills: list[list[str]]) -> MagicMock:
    """Create a mock model that returns a SkillsExtraction with the given skills.

    Args:
        skills: 2D list of skills where inner lists represent OR alternatives
    """
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


class TestExtractMustHaveSkillsNode:
    """Tests for extract_must_have_skills_node function."""

    def test_returns_empty_list_when_no_description(self):
        """Node returns empty skills list when job has no description."""
        mock_factory = MagicMock()
        node = create_extract_must_have_skills_node(mock_factory)

        state = {
            "job": {"job_id": 1, "title": "Developer"},
            "status": "started",
            "cv_context": "Python developer",
        }

        result = node(state)

        assert result["extracted_must_have_skills"] == []

    def test_returns_empty_list_when_description_empty(self):
        """Node returns empty skills list when job description is empty string."""
        mock_factory = MagicMock()
        node = create_extract_must_have_skills_node(mock_factory)

        state = {
            "job": {"job_id": 1, "title": "Developer", "description": ""},
            "status": "started",
            "cv_context": "Python developer",
        }

        result = node(state)

        assert result["extracted_must_have_skills"] == []

    def test_returns_empty_list_on_model_exception(self):
        """Node returns empty skills list when model raises exception."""
        mock_factory = MagicMock()
        mock_factory.get_model.side_effect = Exception("Model unavailable")
        node = create_extract_must_have_skills_node(mock_factory)

        state = {
            "job": {"job_id": 1, "title": "Developer", "description": "Python developer needed"},
            "status": "started",
            "cv_context": "Python developer",
        }

        result = node(state)

        assert result["extracted_must_have_skills"] == []

    def test_handles_result_without_skills_attribute(self):
        """Node handles model result that lacks skills attribute."""
        mock_model = MagicMock()
        mock_structured = MagicMock()
        mock_result = MagicMock(spec=[])  # Object with no attributes
        mock_structured.invoke.return_value = mock_result
        mock_model.with_structured_output.return_value = mock_structured
        mock_factory = _create_mock_factory(mock_model)
        node = create_extract_must_have_skills_node(mock_factory)

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

        assert result["extracted_must_have_skills"] == []

    def test_handles_result_with_none_skills(self):
        """Node handles model result where skills is None."""
        mock_model = MagicMock()
        mock_structured = MagicMock()
        mock_result = MagicMock()
        mock_result.skills = None
        mock_structured.invoke.return_value = mock_result
        mock_model.with_structured_output.return_value = mock_structured
        mock_factory = _create_mock_factory(mock_model)
        node = create_extract_must_have_skills_node(mock_factory)

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

        assert result["extracted_must_have_skills"] == []


class TestExtractMustHaveSkillsNodeWith2DSkillStructure:
    """Tests for extract_must_have_skills_node with 2D skill structure.

    These tests verify the new behavior where skills are returned as a 2D list:
    - Outer list: AND relationships (all groups required)
    - Inner lists: OR relationships (alternatives within a group)
    """

    def test_extracts_solo_skills_as_single_item_groups(self):
        """Node extracts solo skills wrapped in single-item inner lists."""
        expected_skills = [["Python"], ["Django"], ["PostgreSQL"]]
        mock_model = _create_mock_model(expected_skills)
        mock_factory = _create_mock_factory(mock_model)
        node = create_extract_must_have_skills_node(mock_factory)

        state = {
            "job": {
                "job_id": 1,
                "title": "Python Developer",
                "description": "Must have: Python, Django, PostgreSQL",
            },
            "status": "started",
            "cv_context": "Python developer",
        }

        result = node(state)

        assert result["extracted_must_have_skills"] == [["Python"], ["Django"], ["PostgreSQL"]]

    def test_extracts_or_alternatives_as_inner_list(self):
        """Node extracts OR alternatives within the same inner list."""
        expected_skills = [["JavaScript", "Python"], ["React"]]
        mock_model = _create_mock_model(expected_skills)
        mock_factory = _create_mock_factory(mock_model)
        node = create_extract_must_have_skills_node(mock_factory)

        state = {
            "job": {
                "job_id": 1,
                "title": "Frontend Developer",
                "description": "Required: JavaScript or Python, and React",
            },
            "status": "started",
            "cv_context": "Full stack developer",
        }

        result = node(state)

        assert result["extracted_must_have_skills"] == [["JavaScript", "Python"], ["React"]]

    def test_extracts_multiple_or_groups(self):
        """Node extracts multiple OR groups with AND relationship between them."""
        expected_skills = [["JavaScript", "Python"], ["React", "Vue"], ["Docker", "Kubernetes"]]
        mock_model = _create_mock_model(expected_skills)
        mock_factory = _create_mock_factory(mock_model)
        node = create_extract_must_have_skills_node(mock_factory)

        state = {
            "job": {
                "job_id": 1,
                "title": "Full Stack Developer",
                "description": "JS or Python, React or Vue, and Docker or Kubernetes",
            },
            "status": "started",
            "cv_context": "Full stack developer",
        }

        result = node(state)

        assert result["extracted_must_have_skills"] == [
            ["JavaScript", "Python"],
            ["React", "Vue"],
            ["Docker", "Kubernetes"],
        ]

    def test_extracts_mixed_solo_and_or_groups(self):
        """Node extracts combination of solo skills and OR groups."""
        expected_skills = [["JavaScript", "TypeScript"], ["React"], ["PostgreSQL", "MySQL"]]
        mock_model = _create_mock_model(expected_skills)
        mock_factory = _create_mock_factory(mock_model)
        node = create_extract_must_have_skills_node(mock_factory)

        state = {
            "job": {
                "job_id": 1,
                "title": "Developer",
                "description": "JS/TypeScript, React, and PostgreSQL or MySQL",
            },
            "status": "started",
            "cv_context": "Developer",
        }

        result = node(state)

        assert result["extracted_must_have_skills"] == [
            ["JavaScript", "TypeScript"],
            ["React"],
            ["PostgreSQL", "MySQL"],
        ]

    def test_preserves_order_of_skill_groups(self):
        """Node preserves the order of skill groups from LLM output."""
        expected_skills = [["A"], ["B", "C"], ["D"]]
        mock_model = _create_mock_model(expected_skills)
        mock_factory = _create_mock_factory(mock_model)
        node = create_extract_must_have_skills_node(mock_factory)

        state = {
            "job": {
                "job_id": 1,
                "title": "Developer",
                "description": "A, B or C, and D",
            },
            "status": "started",
            "cv_context": "Developer",
        }

        result = node(state)

        assert result["extracted_must_have_skills"] == [["A"], ["B", "C"], ["D"]]

    def test_preserves_order_of_alternatives_within_group(self):
        """Node preserves the order of alternatives within OR groups."""
        expected_skills = [["JavaScript", "TypeScript", "Python"]]
        mock_model = _create_mock_model(expected_skills)
        mock_factory = _create_mock_factory(mock_model)
        node = create_extract_must_have_skills_node(mock_factory)

        state = {
            "job": {
                "job_id": 1,
                "title": "Developer",
                "description": "JavaScript or TypeScript or Python",
            },
            "status": "started",
            "cv_context": "Developer",
        }

        result = node(state)

        assert result["extracted_must_have_skills"][0] == ["JavaScript", "TypeScript", "Python"]

    def test_result_type_is_2d_list(self):
        """Node returns result with 2D list structure (list of lists)."""
        expected_skills = [["Python"]]
        mock_model = _create_mock_model(expected_skills)
        mock_factory = _create_mock_factory(mock_model)
        node = create_extract_must_have_skills_node(mock_factory)

        state = {
            "job": {
                "job_id": 1,
                "title": "Developer",
                "description": "Python developer",
            },
            "status": "started",
            "cv_context": "Developer",
        }

        result = node(state)

        # Verify it's a list of lists, not a flat list
        skills = result["extracted_must_have_skills"]
        assert isinstance(skills, list)
        assert len(skills) > 0
        assert isinstance(skills[0], list)
        assert isinstance(skills[0][0], str)
