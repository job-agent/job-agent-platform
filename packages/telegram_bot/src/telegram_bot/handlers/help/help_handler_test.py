"""Tests for help command handler."""

from telegram_bot.conftest import MockContext, MockMessage, MockUpdate, MockUser
from telegram_bot.handlers.help.handler import help_handler
from telegram_bot.handlers.help.messages import HELP_TEXT


class TestHelpHandler:
    """Tests for help_handler function."""

    async def test_sends_help_text(self):
        """Help handler should send the help text."""
        user = MockUser()
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext()

        await help_handler(update, context)

        assert len(message._reply_texts) == 1
        assert message._reply_texts[0] == HELP_TEXT


class TestHelpText:
    """Tests for HELP_TEXT constant."""

    def test_contains_available_commands_section(self):
        """Help text should have an available commands section."""
        assert "Available Commands" in HELP_TEXT

    def test_lists_start_command(self):
        """Help text should list the /start command."""
        assert "/start" in HELP_TEXT

    def test_lists_help_command(self):
        """Help text should list the /help command."""
        assert "/help" in HELP_TEXT

    def test_lists_search_command(self):
        """Help text should list the /search command."""
        assert "/search" in HELP_TEXT

    def test_lists_status_command(self):
        """Help text should list the /status command."""
        assert "/status" in HELP_TEXT

    def test_lists_cancel_command(self):
        """Help text should list the /cancel command."""
        assert "/cancel" in HELP_TEXT

    def test_contains_cv_upload_instructions(self):
        """Help text should contain CV upload instructions."""
        assert "CV" in HELP_TEXT
        assert "PDF" in HELP_TEXT

    def test_contains_search_examples(self):
        """Help text should contain search examples."""
        assert "min_salary" in HELP_TEXT
        assert "employment_location" in HELP_TEXT

    def test_documents_available_parameters(self):
        """Help text should document available search parameters."""
        assert "min_salary" in HELP_TEXT
        assert "employment_location" in HELP_TEXT
        assert "days" in HELP_TEXT
        assert "timeout" in HELP_TEXT

    def test_lists_search_essays_command(self):
        """Help text should list the /search_essays command."""
        assert "/search_essays" in HELP_TEXT
