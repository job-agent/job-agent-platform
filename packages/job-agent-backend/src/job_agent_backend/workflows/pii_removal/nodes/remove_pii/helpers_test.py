"""Tests for PII removal helpers."""

from unittest.mock import MagicMock, patch

import pytest

from .helpers import anonymize_text


class TestAnonymizeText:
    """Test suite for anonymize_text function."""

    @patch("job_agent_backend.workflows.pii_removal.nodes.remove_pii.helpers.get_model")
    def test_anonymize_text_returns_cleaned_content(self, mock_get_model: MagicMock):
        """Test that anonymize_text returns the model's response content."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Cleaned CV without PII"
        mock_model.invoke.return_value = mock_response
        mock_get_model.return_value = mock_model

        result = anonymize_text("Original CV with PII")

        assert result == "Cleaned CV without PII"
        mock_get_model.assert_called_once_with(model_name="phi3:mini")
        mock_model.invoke.assert_called_once()

    @patch("job_agent_backend.workflows.pii_removal.nodes.remove_pii.helpers.get_model")
    def test_anonymize_text_strips_whitespace(self, mock_get_model: MagicMock):
        """Test that anonymize_text strips leading/trailing whitespace from result."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "  Cleaned content with whitespace  \n"
        mock_model.invoke.return_value = mock_response
        mock_get_model.return_value = mock_model

        result = anonymize_text("Input text")

        assert result == "Cleaned content with whitespace"

    @patch("job_agent_backend.workflows.pii_removal.nodes.remove_pii.helpers.get_model")
    def test_anonymize_text_raises_runtime_error_on_model_failure(self, mock_get_model: MagicMock):
        """Test that anonymize_text raises RuntimeError when model invocation fails."""
        mock_model = MagicMock()
        mock_model.invoke.side_effect = Exception("Model connection failed")
        mock_get_model.return_value = mock_model

        with pytest.raises(RuntimeError, match="Failed to invoke PII anonymization model"):
            anonymize_text("Some CV content")

    @patch("job_agent_backend.workflows.pii_removal.nodes.remove_pii.helpers.get_model")
    def test_anonymize_text_handles_response_without_content_attribute(
        self, mock_get_model: MagicMock
    ):
        """Test that anonymize_text falls back to str() when response has no content attr."""

        class ResponseWithoutContent:
            def __str__(self) -> str:
                return "Fallback string response"

        mock_model = MagicMock()
        mock_model.invoke.return_value = ResponseWithoutContent()
        mock_get_model.return_value = mock_model

        result = anonymize_text("Input CV")

        assert result == "Fallback string response"

    @patch("job_agent_backend.workflows.pii_removal.nodes.remove_pii.helpers.get_model")
    def test_anonymize_text_raises_runtime_error_on_empty_result(self, mock_get_model: MagicMock):
        """Test that anonymize_text raises RuntimeError when result is empty after strip."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "   \n\t  "
        mock_model.invoke.return_value = mock_response
        mock_get_model.return_value = mock_model

        with pytest.raises(RuntimeError, match="PII anonymization returned empty content"):
            anonymize_text("Some CV content")
