"""Tests for start command handler."""

from telegram_bot.conftest import MockContext, MockMessage, MockUpdate, MockUser
from telegram_bot.handlers.start.handler import start_handler
from telegram_bot.handlers.start.messages import get_welcome_message


class TestStartHandler:
    """Tests for start_handler function."""

    async def test_sends_welcome_message_with_user_name(self):
        """Start handler should send welcome message with user's first name."""
        user = MockUser(first_name="Alice")
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext()

        await start_handler(update, context)

        assert len(message._reply_texts) == 1
        assert "Alice" in message._reply_texts[0]
        assert "Job Agent Bot" in message._reply_texts[0]

    async def test_sends_correct_welcome_message_format(self):
        """Start handler should send the expected welcome message."""
        user = MockUser(first_name="Bob")
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext()

        await start_handler(update, context)

        expected = get_welcome_message("Bob")
        assert message._reply_texts[0] == expected


class TestGetWelcomeMessage:
    """Tests for get_welcome_message function."""

    def test_includes_user_name(self):
        """Welcome message should include the user's name."""
        message = get_welcome_message("TestUser")
        assert "TestUser" in message

    def test_includes_greeting(self):
        """Welcome message should include a greeting."""
        message = get_welcome_message("User")
        assert "Hello" in message

    def test_includes_instructions(self):
        """Welcome message should include basic instructions."""
        message = get_welcome_message("User")
        assert "CV" in message
        assert "/search" in message
        assert "/help" in message

    def test_different_names_produce_different_messages(self):
        """Different user names should produce different messages."""
        message1 = get_welcome_message("Alice")
        message2 = get_welcome_message("Bob")
        assert message1 != message2
        assert "Alice" in message1
        assert "Bob" in message2
