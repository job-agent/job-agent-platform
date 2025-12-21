"""Tests for remove_pii_node."""

from unittest.mock import MagicMock, patch

import pytest

from .node import create_remove_pii_node


def _create_mock_factory_with_response(response_content: str) -> MagicMock:
    """Create a mock model factory that returns a model with the given response."""
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.content = response_content
    mock_model.invoke.return_value = mock_response
    mock_factory = MagicMock()
    mock_factory.get_model.return_value = mock_model
    return mock_factory


class TestRemovePiiNode:
    """Test suite for remove_pii_node function."""

    def test_remove_pii_node_returns_anonymized_content(self):
        """Test that remove_pii_node returns state with anonymized cv_context."""
        mock_factory = _create_mock_factory_with_response("Anonymized CV content")
        node = create_remove_pii_node(mock_factory)

        state = {"cv_context": "Original CV with PII"}
        result = node(state)

        assert result == {"cv_context": "Anonymized CV content"}

    def test_remove_pii_node_extracts_job_id_from_state(self, capsys):
        """Test that remove_pii_node extracts job_id from state for logging."""
        mock_factory = _create_mock_factory_with_response("Cleaned")
        node = create_remove_pii_node(mock_factory)

        state = {
            "cv_context": "CV content",
            "job": {"job_id": "job-123", "title": "Software Engineer"},
        }
        node(state)

        captured = capsys.readouterr()
        assert "job-123" in captured.out

    def test_remove_pii_node_handles_missing_job_in_state(self, capsys):
        """Test that remove_pii_node handles state without job field."""
        mock_factory = _create_mock_factory_with_response("Cleaned")
        node = create_remove_pii_node(mock_factory)

        state = {"cv_context": "CV content"}
        node(state)

        captured = capsys.readouterr()
        assert "N/A" in captured.out

    def test_remove_pii_node_handles_job_without_job_id(self, capsys):
        """Test that remove_pii_node handles job dict without job_id."""
        mock_factory = _create_mock_factory_with_response("Cleaned")
        node = create_remove_pii_node(mock_factory)

        state = {"cv_context": "CV content", "job": {"title": "Developer"}}
        node(state)

        captured = capsys.readouterr()
        assert "None" in captured.out

    def test_remove_pii_node_raises_value_error_on_empty_cv_context(self):
        """Test that remove_pii_node raises ValueError when cv_context is empty."""
        mock_factory = MagicMock()
        node = create_remove_pii_node(mock_factory)

        state = {"cv_context": ""}

        with pytest.raises(ValueError, match="No CV context available"):
            node(state)

    def test_remove_pii_node_raises_value_error_on_missing_cv_context(self):
        """Test that remove_pii_node raises ValueError when cv_context is missing."""
        mock_factory = MagicMock()
        node = create_remove_pii_node(mock_factory)

        state = {}

        with pytest.raises(ValueError, match="No CV context available"):
            node(state)

    def test_remove_pii_node_propagates_anonymize_text_exception(self):
        """Test that remove_pii_node propagates exceptions from anonymize_text."""
        mock_model = MagicMock()
        mock_model.invoke.side_effect = Exception("Model error")
        mock_factory = MagicMock()
        mock_factory.get_model.return_value = mock_model
        node = create_remove_pii_node(mock_factory)

        state = {"cv_context": "CV content"}

        with pytest.raises(RuntimeError, match="Failed to invoke PII anonymization model"):
            node(state)
