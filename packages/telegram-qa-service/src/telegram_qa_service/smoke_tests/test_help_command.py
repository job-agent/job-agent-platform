"""Smoke tests for /help command."""

import pytest

pytestmark = pytest.mark.e2e


class TestHelpCommand:
    """E2E tests for the /help bot command."""

    async def test_help_lists_available_commands(self, telegram_qa_client):
        """Bot should respond to /help with a list of available commands.

        Verifies that:
        - The bot is responsive and processes the /help command
        - The response includes references to /search, /status, and /cv commands

        This is a smoke test to verify basic bot functionality and
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
