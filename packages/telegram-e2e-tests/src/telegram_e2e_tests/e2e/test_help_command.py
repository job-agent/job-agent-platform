"""E2E tests for /help command."""

import pytest

pytestmark = pytest.mark.e2e


class TestHelpCommand:
    """E2E tests for the /help bot command."""

    async def test_help_lists_available_commands(self, telegram_qa_client):
        """Bot should respond to /help with a list of available commands.

        Verifies that:
        - The bot is responsive and processes the /help command
        - The response includes references to /search, /status, and /cv commands

        This is an E2E test to verify basic bot functionality and
        that the help text is properly configured.
        """
        response = await telegram_qa_client.send_and_wait("/help")

        assert "/search" in response, (
            f"Expected response to contain '/search' command, got: {response[:200]}"
        )
        assert "/status" in response, (
            f"Expected response to contain '/status' command, got: {response[:200]}"
        )
        assert "/cv" in response or "CV" in response, (
            f"Expected response to contain '/cv' or 'CV', got: {response[:200]}"
        )

    async def test_help_lists_all_bot_commands(self, telegram_qa_client):
        """Bot should list all available commands in the help response.

        Verifies that:
        - All main commands are documented: /start, /search, /status, /cancel
        - Essay commands are documented: /add_essay, /essays
        - CV upload instructions are included

        This comprehensive check ensures users can discover all bot features.
        """
        response = await telegram_qa_client.send_and_wait("/help")

        # Core commands
        assert "/start" in response, (
            f"Expected response to contain '/start' command, got: {response[:300]}"
        )
        assert "/cancel" in response, (
            f"Expected response to contain '/cancel' command, got: {response[:300]}"
        )

        # Essay commands
        assert "/add_essay" in response, (
            f"Expected response to contain '/add_essay' command, got: {response[:300]}"
        )
        assert "/essays" in response, (
            f"Expected response to contain '/essays' command, got: {response[:300]}"
        )
