"""Tests for E2E test helper functions."""

from telegram_e2e_tests.e2e.helpers import extract_essay_id


class TestExtractEssayId:
    """Tests for extract_essay_id helper function."""

    def test_extracts_id_from_success_message(self):
        """Should extract essay ID from standard success message format."""
        response = "Essay saved successfully! (ID: 42)"

        result = extract_essay_id(response)

        assert result == 42

    def test_extracts_id_without_space_after_colon(self):
        """Should extract essay ID when there's no space after colon."""
        response = "Essay saved successfully! (ID:123)"

        result = extract_essay_id(response)

        assert result == 123

    def test_extracts_id_case_insensitive(self):
        """Should extract essay ID regardless of case."""
        response = "Essay saved successfully! (id: 99)"

        result = extract_essay_id(response)

        assert result == 99

    def test_returns_none_when_no_id_present(self):
        """Should return None when response has no ID pattern."""
        response = "Error: Invalid format"

        result = extract_essay_id(response)

        assert result is None

    def test_extracts_first_id_when_multiple_present(self):
        """Should extract the first ID when multiple are present."""
        response = "Essay (ID: 10) referenced by (ID: 20)"

        result = extract_essay_id(response)

        assert result == 10

    def test_handles_empty_string(self):
        """Should return None for empty string."""
        response = ""

        result = extract_essay_id(response)

        assert result is None

    def test_handles_multiline_response(self):
        """Should extract ID from multiline response."""
        response = "Processing...\nEssay saved successfully!\nID: 55"

        result = extract_essay_id(response)

        assert result == 55
