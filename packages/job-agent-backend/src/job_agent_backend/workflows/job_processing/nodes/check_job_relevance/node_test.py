"""Tests for check_job_relevance node."""

from unittest.mock import MagicMock

from .node import create_check_job_relevance_node


def _create_mock_factory_with_model(mock_model: MagicMock) -> MagicMock:
    """Create a mock model factory that returns the given model."""
    mock_factory = MagicMock()
    mock_factory.get_model.return_value = mock_model
    return mock_factory


class TestCheckJobRelevanceNode:
    """Tests for check_job_relevance_node function."""

    def test_returns_relevant_when_no_cv_context(self):
        """Node returns is_relevant=True when CV context is empty."""
        mock_factory = MagicMock()
        node = create_check_job_relevance_node(mock_factory)

        state = {
            "job": {"job_id": 1, "title": "Developer", "description": "Python developer"},
            "status": "started",
            "cv_context": "",
        }

        result = node(state)

        assert result["is_relevant"] is True

    def test_returns_relevant_when_cv_context_missing(self):
        """Node returns is_relevant=True when cv_context key is missing from state."""
        mock_factory = MagicMock()
        node = create_check_job_relevance_node(mock_factory)

        state = {
            "job": {"job_id": 1, "title": "Developer", "description": "Python developer"},
            "status": "started",
        }

        result = node(state)

        assert result["is_relevant"] is True

    def test_returns_relevant_when_no_job_description(self):
        """Node returns is_relevant=True when job has no description."""
        mock_factory = MagicMock()
        node = create_check_job_relevance_node(mock_factory)

        state = {
            "job": {"job_id": 1, "title": "Developer"},
            "status": "started",
            "cv_context": "Python developer with 5 years experience",
        }

        result = node(state)

        assert result["is_relevant"] is True

    def test_returns_relevant_when_job_description_empty(self):
        """Node returns is_relevant=True when job description is empty string."""
        mock_factory = MagicMock()
        node = create_check_job_relevance_node(mock_factory)

        state = {
            "job": {"job_id": 1, "title": "Developer", "description": ""},
            "status": "started",
            "cv_context": "Python developer with 5 years experience",
        }

        result = node(state)

        assert result["is_relevant"] is True

    def test_returns_relevant_on_embedding_exception(self):
        """Node returns is_relevant=True when embedding model raises exception."""
        mock_factory = MagicMock()
        mock_factory.get_model.side_effect = Exception("Model unavailable")
        node = create_check_job_relevance_node(mock_factory)

        state = {
            "job": {"job_id": 1, "title": "Developer", "description": "Python developer"},
            "status": "started",
            "cv_context": "Python developer with 5 years experience",
        }

        result = node(state)

        assert result["is_relevant"] is True

    def test_returns_relevant_when_similarity_above_threshold(
        self, mock_embedding_model_factory
    ):
        """Node returns is_relevant=True when cosine similarity >= 0.4."""
        mock_model = mock_embedding_model_factory(similarity_score=0.5)
        mock_factory = _create_mock_factory_with_model(mock_model)
        node = create_check_job_relevance_node(mock_factory)

        state = {
            "job": {"job_id": 1, "title": "Developer", "description": "Python developer"},
            "status": "started",
            "cv_context": "Python developer with 5 years experience",
        }

        result = node(state)

        assert result["is_relevant"] is True

    def test_returns_relevant_when_similarity_equals_threshold(
        self, mock_embedding_model_factory
    ):
        """Node returns is_relevant=True when cosine similarity equals 0.4 exactly."""
        mock_model = mock_embedding_model_factory(similarity_score=0.4)
        mock_factory = _create_mock_factory_with_model(mock_model)
        node = create_check_job_relevance_node(mock_factory)

        state = {
            "job": {"job_id": 1, "title": "Developer", "description": "Python developer"},
            "status": "started",
            "cv_context": "Python developer with 5 years experience",
        }

        result = node(state)

        assert result["is_relevant"] is True

    def test_returns_irrelevant_when_similarity_below_threshold(
        self, mock_embedding_model_factory
    ):
        """Node returns is_relevant=False when cosine similarity < 0.4."""
        mock_model = mock_embedding_model_factory(similarity_score=0.3)
        mock_factory = _create_mock_factory_with_model(mock_model)
        node = create_check_job_relevance_node(mock_factory)

        state = {
            "job": {"job_id": 1, "title": "Java Architect", "description": "Java developer"},
            "status": "started",
            "cv_context": "Python developer with 5 years experience",
        }

        result = node(state)

        assert result["is_relevant"] is False
