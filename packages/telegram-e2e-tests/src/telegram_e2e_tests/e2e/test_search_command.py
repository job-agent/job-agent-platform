"""E2E tests for /search command."""

import pytest

pytestmark = pytest.mark.e2e


class TestSearchCommand:
    """E2E tests for the /search bot command."""

    async def test_search_command_responds_appropriately(self, telegram_qa_client):
        """Bot should respond to /search command appropriately based on CV state.

        Verifies that:
        - The bot is responsive and processes the /search command
        - When no CV exists, the response indicates the user must upload one first
        - When CV exists, the search process starts

        This is an E2E test to verify the search command is functional.
        """
        response = await telegram_qa_client.send_and_wait("/search")

        response_lower = response.lower()
        # Accept either CV required message or search starting message
        has_cv_required = "no cv" in response_lower or "upload" in response_lower
        has_search_started = "search" in response_lower or "job" in response_lower
        assert has_cv_required or has_search_started, (
            f"Expected search-related response, got: {response[:200]}"
        )

    async def test_search_with_invalid_min_salary_responds(self, telegram_qa_client):
        """Bot should respond to /search with invalid min_salary parameter.

        Verifies that:
        - The bot processes the command even with invalid parameter
        - The bot either shows an error or ignores the invalid value and proceeds
        - The bot remains responsive

        This E2E test verifies the bot handles edge cases gracefully.
        """
        response = await telegram_qa_client.send_and_wait("/search min_salary=invalid")

        response_lower = response.lower()
        # Accept either: error message, or search proceeds (ignoring invalid param)
        has_error = "error" in response_lower or "invalid" in response_lower
        has_search_response = "search" in response_lower or "job" in response_lower
        assert has_error or has_search_response, (
            f"Expected error or search response, got: {response[:200]}"
        )

    async def test_search_with_deprecated_salary_param_shows_migration_hint(
        self, telegram_qa_client
    ):
        """Bot should respond with helpful message when deprecated 'salary' param is used.

        Verifies that:
        - The bot detects use of the deprecated 'salary' parameter
        - The response suggests using 'min_salary' instead
        - Users get clear guidance on the correct parameter name

        This helps users migrate from old command syntax.
        """
        response = await telegram_qa_client.send_and_wait("/search salary=5000")

        response_lower = response.lower()
        assert "min_salary" in response_lower or "no longer supported" in response_lower, (
            f"Expected response to mention min_salary or deprecation, got: {response[:200]}"
        )
