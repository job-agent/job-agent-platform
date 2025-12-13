"""Tests for check_job_relevance node."""

from unittest.mock import patch, MagicMock

import numpy as np

from .node import check_job_relevance_node


def _create_mock_embedding_model(similarity_score: float) -> MagicMock:
    """
    Create a mock embedding model that produces embeddings with the desired cosine similarity.

    Args:
        similarity_score: The desired cosine similarity between CV and job embeddings.
    """
    mock_model = MagicMock()

    cv_embedding = np.array([1.0, 0.0, 0.0])
    job_embedding = np.array([similarity_score, np.sqrt(1 - similarity_score**2), 0.0])

    cv_embedding = cv_embedding / np.linalg.norm(cv_embedding)
    job_embedding = job_embedding / np.linalg.norm(job_embedding)

    mock_model.embed_query.side_effect = [cv_embedding.tolist(), job_embedding.tolist()]

    return mock_model


class TestCheckJobRelevanceNode:
    """Tests for check_job_relevance_node function."""

    def test_returns_relevant_when_no_cv_context(self):
        """Node returns is_relevant=True when CV context is empty."""
        state = {
            "job": {"job_id": 1, "title": "Developer", "description": "Python developer"},
            "status": "started",
            "cv_context": "",
        }

        result = check_job_relevance_node(state)

        assert result["is_relevant"] is True

    def test_returns_relevant_when_cv_context_missing(self):
        """Node returns is_relevant=True when cv_context key is missing from state."""
        state = {
            "job": {"job_id": 1, "title": "Developer", "description": "Python developer"},
            "status": "started",
        }

        result = check_job_relevance_node(state)

        assert result["is_relevant"] is True

    def test_returns_relevant_when_no_job_description(self):
        """Node returns is_relevant=True when job has no description."""
        state = {
            "job": {"job_id": 1, "title": "Developer"},
            "status": "started",
            "cv_context": "Python developer with 5 years experience",
        }

        result = check_job_relevance_node(state)

        assert result["is_relevant"] is True

    def test_returns_relevant_when_job_description_empty(self):
        """Node returns is_relevant=True when job description is empty string."""
        state = {
            "job": {"job_id": 1, "title": "Developer", "description": ""},
            "status": "started",
            "cv_context": "Python developer with 5 years experience",
        }

        result = check_job_relevance_node(state)

        assert result["is_relevant"] is True

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.get_model")
    def test_returns_relevant_on_embedding_exception(self, mock_get_model):
        """Node returns is_relevant=True when embedding model raises exception."""
        mock_get_model.side_effect = Exception("Model unavailable")

        state = {
            "job": {"job_id": 1, "title": "Developer", "description": "Python developer"},
            "status": "started",
            "cv_context": "Python developer with 5 years experience",
        }

        result = check_job_relevance_node(state)

        assert result["is_relevant"] is True

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.get_model")
    def test_returns_relevant_when_similarity_above_threshold(self, mock_get_model):
        """Node returns is_relevant=True when cosine similarity >= 0.4."""
        mock_get_model.return_value = _create_mock_embedding_model(similarity_score=0.5)

        state = {
            "job": {"job_id": 1, "title": "Developer", "description": "Python developer"},
            "status": "started",
            "cv_context": "Python developer with 5 years experience",
        }

        result = check_job_relevance_node(state)

        assert result["is_relevant"] is True

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.get_model")
    def test_returns_relevant_when_similarity_equals_threshold(self, mock_get_model):
        """Node returns is_relevant=True when cosine similarity equals 0.4 exactly."""
        mock_get_model.return_value = _create_mock_embedding_model(similarity_score=0.4)

        state = {
            "job": {"job_id": 1, "title": "Developer", "description": "Python developer"},
            "status": "started",
            "cv_context": "Python developer with 5 years experience",
        }

        result = check_job_relevance_node(state)

        assert result["is_relevant"] is True

    @patch("job_agent_backend.workflows.job_processing.nodes.check_job_relevance.node.get_model")
    def test_returns_irrelevant_when_similarity_below_threshold(self, mock_get_model):
        """Node returns is_relevant=False when cosine similarity < 0.4."""
        mock_get_model.return_value = _create_mock_embedding_model(similarity_score=0.3)

        state = {
            "job": {"job_id": 1, "title": "Java Architect", "description": "Java developer"},
            "status": "started",
            "cv_context": "Python developer with 5 years experience",
        }

        result = check_job_relevance_node(state)

        assert result["is_relevant"] is False
