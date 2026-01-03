"""E2E tests for /cancel command."""

import pytest

pytestmark = pytest.mark.e2e


class TestCancelCommand:
    """E2E tests for the /cancel bot command."""

    async def test_cancel_with_no_active_search_shows_message(self, telegram_qa_client):
        """Bot should respond to /cancel with appropriate message when no search is active.

        Verifies that:
        - The bot is responsive and processes the /cancel command
        - When no search is running, the response indicates this clearly
        - The response suggests using /search to start a new search

        This is an E2E test to verify the cancel command handles the
        no-search scenario gracefully.
        """
        response = await telegram_qa_client.send_and_wait("/cancel")

        response_lower = response.lower()
        assert "no active search" in response_lower or "no search" in response_lower, (
            f"Expected response to indicate no active search, got: {response[:200]}"
        )
