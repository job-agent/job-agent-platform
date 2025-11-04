"""Integration tests for PII removal workflow."""

from unittest.mock import patch, MagicMock
import pytest

from job_agent_backend.workflows import run_pii_removal


class TestPIIRemovalWorkflow:
    """Test suite for PII removal workflow."""

    @patch("job_agent_backend.workflows.pii_removal.nodes.remove_pii.node.ChatOpenAI")
    def test_pii_removal_with_valid_cv(self, mock_chat_openai, sample_cv_with_pii):
        """Test PII removal with valid CV content."""

        mock_llm_instance = MagicMock()
        mock_structured_llm = MagicMock()
        mock_result = MagicMock()
        mock_result.professional_content = """
        [REDACTED]
        Email: [REDACTED]
        Phone: [REDACTED]
        Address: [REDACTED]

        Professional Experience:
        - 5+ years of Python development at [COMPANY]
        - Led team of engineers
        """
        mock_structured_llm.invoke.return_value = mock_result
        mock_llm_instance.with_structured_output.return_value = mock_structured_llm
        mock_chat_openai.return_value = mock_llm_instance

        result = run_pii_removal(sample_cv_with_pii)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "[REDACTED]" in result or "[COMPANY]" in result

        mock_structured_llm.invoke.assert_called_once()

    @patch("job_agent_backend.workflows.pii_removal.nodes.remove_pii.node.ChatOpenAI")
    def test_pii_removal_preserves_professional_content(self, mock_chat_openai, sample_cv_content):
        """Test that PII removal preserves professional content."""

        mock_llm_instance = MagicMock()
        mock_structured_llm = MagicMock()
        mock_result = MagicMock()
        mock_result.professional_content = sample_cv_content
        mock_structured_llm.invoke.return_value = mock_result
        mock_llm_instance.with_structured_output.return_value = mock_structured_llm
        mock_chat_openai.return_value = mock_llm_instance

        result = run_pii_removal(sample_cv_content)

        assert "Python" in result
        assert "Django" in result or "development" in result
        assert len(result) > 0

    def test_pii_removal_with_empty_cv_raises_error(self):
        """Test that empty CV content raises ValueError."""
        with pytest.raises(ValueError, match="CV content is required"):
            run_pii_removal("")

    def test_pii_removal_with_none_cv_raises_error(self):
        """Test that None CV content raises ValueError."""
        with pytest.raises(ValueError, match="CV content is required"):
            run_pii_removal(None)

    @patch("job_agent_backend.workflows.pii_removal.nodes.remove_pii.node.ChatOpenAI")
    def test_pii_removal_with_minimal_cv(self, mock_chat_openai):
        """Test PII removal with minimal CV content."""
        minimal_cv = "Software Engineer with 3 years experience."

        mock_llm_instance = MagicMock()
        mock_structured_llm = MagicMock()
        mock_result = MagicMock()
        mock_result.professional_content = minimal_cv
        mock_structured_llm.invoke.return_value = mock_result
        mock_llm_instance.with_structured_output.return_value = mock_structured_llm
        mock_chat_openai.return_value = mock_llm_instance

        result = run_pii_removal(minimal_cv)

        assert isinstance(result, str)
        assert len(result) > 0

    @patch("job_agent_backend.workflows.pii_removal.nodes.remove_pii.node.ChatOpenAI")
    def test_pii_removal_workflow_state_transitions(self, mock_chat_openai, sample_cv_content):
        """Test that workflow properly transitions through states."""
        mock_llm_instance = MagicMock()
        mock_structured_llm = MagicMock()
        mock_result = MagicMock()
        mock_result.professional_content = "Cleaned CV content"
        mock_structured_llm.invoke.return_value = mock_result
        mock_llm_instance.with_structured_output.return_value = mock_structured_llm
        mock_chat_openai.return_value = mock_llm_instance

        result = run_pii_removal(sample_cv_content)

        assert result == "Cleaned CV content"
        mock_structured_llm.invoke.assert_called_once()

    @patch("job_agent_backend.workflows.pii_removal.nodes.remove_pii.node.ChatOpenAI")
    def test_pii_removal_handles_special_characters(self, mock_chat_openai):
        """Test PII removal with special characters in CV."""
        cv_with_special_chars = """
        Email: test@example.com
        Skills: C++, C#, .NET
        Experience: 5+ years
        """

        mock_llm_instance = MagicMock()
        mock_structured_llm = MagicMock()
        mock_result = MagicMock()
        mock_result.professional_content = """
        Email: [REDACTED]
        Skills: C++, C#, .NET
        Experience: 5+ years
        """
        mock_structured_llm.invoke.return_value = mock_result
        mock_llm_instance.with_structured_output.return_value = mock_structured_llm
        mock_chat_openai.return_value = mock_llm_instance

        result = run_pii_removal(cv_with_special_chars)

        assert isinstance(result, str)
        assert "C++" in result or "Skills" in result

    @patch("job_agent_backend.workflows.pii_removal.nodes.remove_pii.node.ChatOpenAI")
    def test_pii_removal_with_unicode_characters(self, mock_chat_openai):
        """Test PII removal with unicode characters."""
        cv_with_unicode = """
        Name: José García
        Email: josé@example.com
        Skills: Python, データサイエンス
        """

        mock_llm_instance = MagicMock()
        mock_structured_llm = MagicMock()
        mock_result = MagicMock()
        mock_result.professional_content = """
        Name: [REDACTED]
        Email: [REDACTED]
        Skills: Python, データサイエンス
        """
        mock_structured_llm.invoke.return_value = mock_result
        mock_llm_instance.with_structured_output.return_value = mock_structured_llm
        mock_chat_openai.return_value = mock_llm_instance

        result = run_pii_removal(cv_with_unicode)

        assert isinstance(result, str)
        assert len(result) > 0

    @patch("job_agent_backend.workflows.pii_removal.nodes.remove_pii.node.ChatOpenAI")
    def test_pii_removal_with_long_cv(self, mock_chat_openai):
        """Test PII removal with long CV content."""
        long_cv = "\n".join(
            [f"Professional Experience {i}: Worked on project {i}" for i in range(100)]
        )

        mock_llm_instance = MagicMock()
        mock_structured_llm = MagicMock()
        mock_result = MagicMock()
        mock_result.professional_content = "Cleaned long CV"
        mock_structured_llm.invoke.return_value = mock_result
        mock_llm_instance.with_structured_output.return_value = mock_structured_llm
        mock_chat_openai.return_value = mock_llm_instance

        result = run_pii_removal(long_cv)

        assert isinstance(result, str)
        assert len(result) > 0
        mock_structured_llm.invoke.assert_called_once()

    @patch("job_agent_backend.workflows.pii_removal.nodes.remove_pii.node.ChatOpenAI")
    def test_pii_removal_model_is_invoked_with_correct_input(
        self, mock_chat_openai, sample_cv_with_pii
    ):
        """Test that the model is invoked with correct input."""
        mock_llm_instance = MagicMock()
        mock_structured_llm = MagicMock()
        mock_result = MagicMock()
        mock_result.professional_content = "Cleaned CV"
        mock_structured_llm.invoke.return_value = mock_result
        mock_llm_instance.with_structured_output.return_value = mock_structured_llm
        mock_chat_openai.return_value = mock_llm_instance

        run_pii_removal(sample_cv_with_pii)

        assert mock_structured_llm.invoke.called

    @patch("job_agent_backend.workflows.pii_removal.nodes.remove_pii.node.ChatOpenAI")
    def test_pii_removal_returns_string_not_state(self, mock_chat_openai, sample_cv_content):
        """Test that workflow returns cleaned string, not state object."""
        mock_llm_instance = MagicMock()
        mock_structured_llm = MagicMock()
        mock_result = MagicMock()
        mock_result.professional_content = "Cleaned content"
        mock_structured_llm.invoke.return_value = mock_result
        mock_llm_instance.with_structured_output.return_value = mock_structured_llm
        mock_chat_openai.return_value = mock_llm_instance

        result = run_pii_removal(sample_cv_content)

        assert isinstance(result, str)
        assert result == "Cleaned content"
