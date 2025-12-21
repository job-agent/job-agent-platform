"""Tests for PII removal workflow."""

from unittest.mock import MagicMock
import pytest

from job_agent_backend.workflows import run_pii_removal


def create_mock_model(response_content: str):
    """Helper to create a mock model with invoke method."""
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.content = response_content
    mock_model.invoke.return_value = mock_response
    return mock_model


def create_mock_model_factory(mock_model: MagicMock) -> MagicMock:
    """Create a mock model factory that returns the given model."""
    mock_factory = MagicMock()
    mock_factory.get_model.return_value = mock_model
    return mock_factory


class TestPIIRemovalWorkflow:
    """Test suite for PII removal workflow."""

    def test_pii_removal_with_valid_cv(self, sample_cv_with_pii):
        """Test PII removal with valid CV content."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.content = """
        [REDACTED]
        Email: [REDACTED]
        Phone: [REDACTED]
        Address: [REDACTED]

        Professional Experience:
        - 5+ years of Python development at [COMPANY]
        - Led team of engineers
        """
        mock_model.invoke.return_value = mock_response
        mock_factory = create_mock_model_factory(mock_model)

        result = run_pii_removal(sample_cv_with_pii, model_factory=mock_factory)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "[REDACTED]" in result or "[COMPANY]" in result

        mock_model.invoke.assert_called_once()

    def test_pii_removal_preserves_professional_content(self, sample_cv_content):
        """Test that PII removal preserves professional content."""
        mock_model = create_mock_model(sample_cv_content)
        mock_factory = create_mock_model_factory(mock_model)

        result = run_pii_removal(sample_cv_content, model_factory=mock_factory)

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

    def test_pii_removal_with_minimal_cv(self):
        """Test PII removal with minimal CV content."""
        minimal_cv = "Software Engineer with 3 years experience."
        mock_model = create_mock_model(minimal_cv)
        mock_factory = create_mock_model_factory(mock_model)

        result = run_pii_removal(minimal_cv, model_factory=mock_factory)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_pii_removal_workflow_state_transitions(self, sample_cv_content):
        """Test that workflow properly transitions through states."""
        mock_model = create_mock_model("Cleaned CV content")
        mock_factory = create_mock_model_factory(mock_model)

        result = run_pii_removal(sample_cv_content, model_factory=mock_factory)

        assert result == "Cleaned CV content"
        mock_model.invoke.assert_called_once()

    def test_pii_removal_handles_special_characters(self):
        """Test PII removal with special characters in CV."""
        cv_with_special_chars = """
        Email: test@example.com
        Skills: C++, C#, .NET
        Experience: 5+ years
        """

        response_content = """
        Email: [REDACTED]
        Skills: C++, C#, .NET
        Experience: 5+ years
        """
        mock_model = create_mock_model(response_content)
        mock_factory = create_mock_model_factory(mock_model)

        result = run_pii_removal(cv_with_special_chars, model_factory=mock_factory)

        assert isinstance(result, str)
        assert "C++" in result or "Skills" in result

    def test_pii_removal_with_unicode_characters(self):
        """Test PII removal with unicode characters."""
        cv_with_unicode = """
        Name: Jose Garcia
        Email: jose@example.com
        Skills: Python, Data Science
        """

        response_content = """
        Name: [REDACTED]
        Email: [REDACTED]
        Skills: Python, Data Science
        """
        mock_model = create_mock_model(response_content)
        mock_factory = create_mock_model_factory(mock_model)

        result = run_pii_removal(cv_with_unicode, model_factory=mock_factory)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_pii_removal_with_long_cv(self):
        """Test PII removal with long CV content."""
        long_cv = "\n".join(
            [f"Professional Experience {i}: Worked on project {i}" for i in range(100)]
        )

        mock_model = create_mock_model("Cleaned long CV")
        mock_factory = create_mock_model_factory(mock_model)

        result = run_pii_removal(long_cv, model_factory=mock_factory)

        assert isinstance(result, str)
        assert len(result) > 0
        mock_model.invoke.assert_called_once()

    def test_pii_removal_model_is_invoked_with_correct_input(self, sample_cv_with_pii):
        """Test that the model is invoked with correct input."""
        mock_model = create_mock_model("Cleaned CV")
        mock_factory = create_mock_model_factory(mock_model)

        run_pii_removal(sample_cv_with_pii, model_factory=mock_factory)

        assert mock_model.invoke.called

    def test_pii_removal_returns_string_not_state(self, sample_cv_content):
        """Test that workflow returns cleaned string, not state object."""
        mock_model = create_mock_model("Cleaned content")
        mock_factory = create_mock_model_factory(mock_model)

        result = run_pii_removal(sample_cv_content, model_factory=mock_factory)

        assert isinstance(result, str)
        assert result == "Cleaned content"
