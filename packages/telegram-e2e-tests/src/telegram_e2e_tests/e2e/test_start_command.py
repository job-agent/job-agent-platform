"""E2E tests for /start command."""

import pytest

pytestmark = pytest.mark.e2e


class TestStartCommand:
    """E2E tests for the /start bot command."""

    async def test_start_responds_with_welcome(self, telegram_qa_client):
        """Bot should respond to /start with a welcome message.

        Verifies that:
        - The bot is responsive and processes the /start command
        - The response contains either "Job Agent" or "welcome" (case-insensitive)

        This is an E2E test to verify basic bot functionality.
        """
        response = await telegram_qa_client.send_and_wait("/start")

        response_lower = response.lower()
        assert "job agent" in response_lower or "welcome" in response_lower, (
            f"Expected response to contain 'Job Agent' or 'welcome', got: {response[:200]}"
        )
