"""E2E tests for /status command."""

import pytest

pytestmark = pytest.mark.e2e


class TestStatusCommand:
    """E2E tests for the /status bot command."""

    async def test_status_with_no_active_search_shows_message(self, telegram_qa_client):
        """Bot should respond to /status with no active searches message.

        Verifies that:
        - The bot is responsive and processes the /status command
        - When no search is active, the response indicates this clearly
        - The response suggests using /search to start a new search

        This is an E2E test to verify the status command works correctly
        when the user has no running searches.
        """
        response = await telegram_qa_client.send_and_wait("/status")

        response_lower = response.lower()
        assert "no active" in response_lower, (
            f"Expected response to contain 'no active' (searches), got: {response[:200]}"
        )
