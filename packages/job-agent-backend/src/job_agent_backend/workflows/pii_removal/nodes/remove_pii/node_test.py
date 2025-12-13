"""Tests for remove_pii_node."""

from unittest.mock import MagicMock, patch

import pytest

from .node import remove_pii_node


class TestRemovePiiNode:
    """Test suite for remove_pii_node function."""

    @patch("job_agent_backend.workflows.pii_removal.nodes.remove_pii.node.anonymize_text")
    def test_remove_pii_node_returns_anonymized_content(self, mock_anonymize_text: MagicMock):
        """Test that remove_pii_node returns state with anonymized cv_context."""
        mock_anonymize_text.return_value = "Anonymized CV content"
        state = {"cv_context": "Original CV with PII"}

        result = remove_pii_node(state)

        assert result == {"cv_context": "Anonymized CV content"}
        mock_anonymize_text.assert_called_once_with("Original CV with PII")

    @patch("job_agent_backend.workflows.pii_removal.nodes.remove_pii.node.anonymize_text")
    def test_remove_pii_node_extracts_job_id_from_state(
        self, mock_anonymize_text: MagicMock, capsys
    ):
        """Test that remove_pii_node extracts job_id from state for logging."""
        mock_anonymize_text.return_value = "Cleaned"
        state = {
            "cv_context": "CV content",
            "job": {"job_id": "job-123", "title": "Software Engineer"},
        }

        remove_pii_node(state)

        captured = capsys.readouterr()
        assert "job-123" in captured.out

    @patch("job_agent_backend.workflows.pii_removal.nodes.remove_pii.node.anonymize_text")
    def test_remove_pii_node_handles_missing_job_in_state(
        self, mock_anonymize_text: MagicMock, capsys
    ):
        """Test that remove_pii_node handles state without job field."""
        mock_anonymize_text.return_value = "Cleaned"
        state = {"cv_context": "CV content"}

        remove_pii_node(state)

        captured = capsys.readouterr()
        assert "N/A" in captured.out

    @patch("job_agent_backend.workflows.pii_removal.nodes.remove_pii.node.anonymize_text")
    def test_remove_pii_node_handles_job_without_job_id(
        self, mock_anonymize_text: MagicMock, capsys
    ):
        """Test that remove_pii_node handles job dict without job_id."""
        mock_anonymize_text.return_value = "Cleaned"
        state = {"cv_context": "CV content", "job": {"title": "Developer"}}

        remove_pii_node(state)

        captured = capsys.readouterr()
        assert "None" in captured.out

    def test_remove_pii_node_raises_value_error_on_empty_cv_context(self):
        """Test that remove_pii_node raises ValueError when cv_context is empty."""
        state = {"cv_context": ""}

        with pytest.raises(ValueError, match="No CV context available"):
            remove_pii_node(state)

    def test_remove_pii_node_raises_value_error_on_missing_cv_context(self):
        """Test that remove_pii_node raises ValueError when cv_context is missing."""
        state = {}

        with pytest.raises(ValueError, match="No CV context available"):
            remove_pii_node(state)

    @patch("job_agent_backend.workflows.pii_removal.nodes.remove_pii.node.anonymize_text")
    def test_remove_pii_node_propagates_anonymize_text_exception(
        self, mock_anonymize_text: MagicMock
    ):
        """Test that remove_pii_node propagates exceptions from anonymize_text."""
        mock_anonymize_text.side_effect = RuntimeError("Anonymization failed")
        state = {"cv_context": "CV content"}

        with pytest.raises(RuntimeError, match="Anonymization failed"):
            remove_pii_node(state)
