"""Tests for extract_nice_to_have_skills node."""

from unittest.mock import MagicMock

from .node import create_extract_nice_to_have_skills_node
from ..extract_must_have_skills.schemas import SkillsExtraction


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


class TestExtractNiceToHaveSkillsNodeWith2DSkillStructure:
    """Tests for extract_nice_to_have_skills_node with 2D skill structure.

    These tests verify the new behavior where skills are returned as a 2D list:
    - Outer list: AND relationships (all groups desirable)
    - Inner lists: OR relationships (alternatives within a group)
    """

    def test_extracts_solo_skills_as_single_item_groups(self):
        """Node extracts solo skills wrapped in single-item inner lists."""
        expected_skills = [["Docker"], ["Kubernetes"], ["AWS"]]
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

        assert result["extracted_nice_to_have_skills"] == [["Docker"], ["Kubernetes"], ["AWS"]]

    def test_extracts_or_alternatives_as_inner_list(self):
        """Node extracts OR alternatives within the same inner list."""
        expected_skills = [["AWS", "GCP"], ["Terraform"]]
        mock_model = _create_mock_model(expected_skills)
        mock_factory = _create_mock_factory(mock_model)
        node = create_extract_nice_to_have_skills_node(mock_factory)

        state = {
            "job": {
                "job_id": 1,
                "title": "DevOps Engineer",
                "description": "Preferred: AWS or GCP, and Terraform experience",
            },
            "status": "started",
            "cv_context": "DevOps engineer",
        }

        result = node(state)

        assert result["extracted_nice_to_have_skills"] == [["AWS", "GCP"], ["Terraform"]]

    def test_extracts_multiple_or_groups(self):
        """Node extracts multiple OR groups with AND relationship between them."""
        expected_skills = [["React", "Vue"], ["GraphQL", "REST"], ["Jest", "Mocha"]]
        mock_model = _create_mock_model(expected_skills)
        mock_factory = _create_mock_factory(mock_model)
        node = create_extract_nice_to_have_skills_node(mock_factory)

        state = {
            "job": {
                "job_id": 1,
                "title": "Frontend Developer",
                "description": "Preferred: React or Vue, GraphQL or REST, Jest or Mocha",
            },
            "status": "started",
            "cv_context": "Frontend developer",
        }

        result = node(state)

        assert result["extracted_nice_to_have_skills"] == [
            ["React", "Vue"],
            ["GraphQL", "REST"],
            ["Jest", "Mocha"],
        ]

    def test_extracts_mixed_solo_and_or_groups(self):
        """Node extracts combination of solo skills and OR groups."""
        expected_skills = [["Redis", "Memcached"], ["Grafana"], ["Prometheus", "DataDog"]]
        mock_model = _create_mock_model(expected_skills)
        mock_factory = _create_mock_factory(mock_model)
        node = create_extract_nice_to_have_skills_node(mock_factory)

        state = {
            "job": {
                "job_id": 1,
                "title": "SRE",
                "description": "Preferred: Redis/Memcached, Grafana, Prometheus or DataDog",
            },
            "status": "started",
            "cv_context": "Site reliability engineer",
        }

        result = node(state)

        assert result["extracted_nice_to_have_skills"] == [
            ["Redis", "Memcached"],
            ["Grafana"],
            ["Prometheus", "DataDog"],
        ]

    def test_preserves_order_of_skill_groups(self):
        """Node preserves the order of skill groups from LLM output."""
        expected_skills = [["X"], ["Y", "Z"], ["W"]]
        mock_model = _create_mock_model(expected_skills)
        mock_factory = _create_mock_factory(mock_model)
        node = create_extract_nice_to_have_skills_node(mock_factory)

        state = {
            "job": {
                "job_id": 1,
                "title": "Developer",
                "description": "Nice to have: X, Y or Z, W",
            },
            "status": "started",
            "cv_context": "Developer",
        }

        result = node(state)

        assert result["extracted_nice_to_have_skills"] == [["X"], ["Y", "Z"], ["W"]]

    def test_preserves_order_of_alternatives_within_group(self):
        """Node preserves the order of alternatives within OR groups."""
        expected_skills = [["AWS", "GCP", "Azure"]]
        mock_model = _create_mock_model(expected_skills)
        mock_factory = _create_mock_factory(mock_model)
        node = create_extract_nice_to_have_skills_node(mock_factory)

        state = {
            "job": {
                "job_id": 1,
                "title": "Cloud Engineer",
                "description": "Nice to have: AWS or GCP or Azure",
            },
            "status": "started",
            "cv_context": "Cloud engineer",
        }

        result = node(state)

        assert result["extracted_nice_to_have_skills"][0] == ["AWS", "GCP", "Azure"]

    def test_result_type_is_2d_list(self):
        """Node returns result with 2D list structure (list of lists)."""
        expected_skills = [["Docker"]]
        mock_model = _create_mock_model(expected_skills)
        mock_factory = _create_mock_factory(mock_model)
        node = create_extract_nice_to_have_skills_node(mock_factory)

        state = {
            "job": {
                "job_id": 1,
                "title": "Developer",
                "description": "Nice to have: Docker experience",
            },
            "status": "started",
            "cv_context": "Developer",
        }

        result = node(state)

        # Verify it's a list of lists, not a flat list
        skills = result["extracted_nice_to_have_skills"]
        assert isinstance(skills, list)
        assert len(skills) > 0
        assert isinstance(skills[0], list)
        assert isinstance(skills[0][0], str)
