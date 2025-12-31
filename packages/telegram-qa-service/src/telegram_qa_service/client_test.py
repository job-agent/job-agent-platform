"""Tests for TelegramQAClient."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestTelegramQAClientConstruction:
    """Tests for TelegramQAClient initialization."""

    def test_loads_config_on_construction(self):
        """Client should load configuration when constructed."""
        from telegram_qa_service.client import TelegramQAClient
        from telegram_qa_service.config import QAConfig

        env = {
            "TELEGRAM_API_ID": "12345678",
            "TELEGRAM_API_HASH": "abcdef1234567890",
            "TELEGRAM_QA_BOT_USERNAME": "@test_bot",
        }
        with patch.dict(os.environ, env, clear=True):
            client = TelegramQAClient()

        assert isinstance(client.config, QAConfig)
        assert client.config.api_id == 12345678

    def test_raises_configuration_error_when_config_invalid(self):
        """Client should raise ConfigurationError when environment is incomplete."""
        from telegram_qa_service.client import TelegramQAClient
        from telegram_qa_service.exceptions import ConfigurationError

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ConfigurationError):
                TelegramQAClient()


class TestTelegramQAClientContextManager:
    """Tests for TelegramQAClient async context manager behavior."""

    async def test_connects_on_enter(self):
        """Client should connect to Telegram when entering context."""
        from telegram_qa_service.client import TelegramQAClient

        env = {
            "TELEGRAM_API_ID": "12345678",
            "TELEGRAM_API_HASH": "abcdef1234567890",
            "TELEGRAM_QA_BOT_USERNAME": "@test_bot",
        }
        mock_telethon_client = AsyncMock()
        mock_telethon_client.connect = AsyncMock()
        mock_telethon_client.is_user_authorized = AsyncMock(return_value=True)

        with patch.dict(os.environ, env, clear=True):
            with patch(
                "telegram_qa_service.client.TelegramClient",
                return_value=mock_telethon_client,
            ):
                client = TelegramQAClient()
                async with client:
                    mock_telethon_client.connect.assert_called_once()

    async def test_disconnects_on_exit(self):
        """Client should disconnect from Telegram when exiting context."""
        from telegram_qa_service.client import TelegramQAClient

        env = {
            "TELEGRAM_API_ID": "12345678",
            "TELEGRAM_API_HASH": "abcdef1234567890",
            "TELEGRAM_QA_BOT_USERNAME": "@test_bot",
        }
        mock_telethon_client = AsyncMock()
        mock_telethon_client.connect = AsyncMock()
        mock_telethon_client.disconnect = AsyncMock()
        mock_telethon_client.is_user_authorized = AsyncMock(return_value=True)

        with patch.dict(os.environ, env, clear=True):
            with patch(
                "telegram_qa_service.client.TelegramClient",
                return_value=mock_telethon_client,
            ):
                client = TelegramQAClient()
                async with client:
                    pass
                mock_telethon_client.disconnect.assert_called_once()

    async def test_disconnects_on_exception(self):
        """Client should disconnect even when exception occurs in context."""
        from telegram_qa_service.client import TelegramQAClient

        env = {
            "TELEGRAM_API_ID": "12345678",
            "TELEGRAM_API_HASH": "abcdef1234567890",
            "TELEGRAM_QA_BOT_USERNAME": "@test_bot",
        }
        mock_telethon_client = AsyncMock()
        mock_telethon_client.connect = AsyncMock()
        mock_telethon_client.disconnect = AsyncMock()
        mock_telethon_client.is_user_authorized = AsyncMock(return_value=True)

        with patch.dict(os.environ, env, clear=True):
            with patch(
                "telegram_qa_service.client.TelegramClient",
                return_value=mock_telethon_client,
            ):
                client = TelegramQAClient()
                with pytest.raises(ValueError):
                    async with client:
                        raise ValueError("test error")

                mock_telethon_client.disconnect.assert_called_once()

    async def test_raises_connection_error_on_connect_failure(self):
        """Client should raise ConnectionError when Telegram connection fails."""
        from telegram_qa_service.client import TelegramQAClient
        from telegram_qa_service.exceptions import ConnectionError

        env = {
            "TELEGRAM_API_ID": "12345678",
            "TELEGRAM_API_HASH": "abcdef1234567890",
            "TELEGRAM_QA_BOT_USERNAME": "@test_bot",
        }
        mock_telethon_client = AsyncMock()
        mock_telethon_client.connect = AsyncMock(side_effect=Exception("Network error"))

        with patch.dict(os.environ, env, clear=True):
            with patch(
                "telegram_qa_service.client.TelegramClient",
                return_value=mock_telethon_client,
            ):
                client = TelegramQAClient()
                with pytest.raises(ConnectionError) as exc_info:
                    async with client:
                        pass

                assert "connect" in str(exc_info.value).lower()


class TestTelegramQAClientSendCommand:
    """Tests for TelegramQAClient.send_command method."""

    async def test_sends_message_to_bot(self):
        """send_command should send message to configured bot username."""
        from telegram_qa_service.client import TelegramQAClient

        env = {
            "TELEGRAM_API_ID": "12345678",
            "TELEGRAM_API_HASH": "abcdef1234567890",
            "TELEGRAM_QA_BOT_USERNAME": "@test_bot",
        }
        mock_telethon_client = AsyncMock()
        mock_telethon_client.connect = AsyncMock()
        mock_telethon_client.disconnect = AsyncMock()
        mock_telethon_client.is_user_authorized = AsyncMock(return_value=True)
        mock_telethon_client.send_message = AsyncMock()

        with patch.dict(os.environ, env, clear=True):
            with patch(
                "telegram_qa_service.client.TelegramClient",
                return_value=mock_telethon_client,
            ):
                client = TelegramQAClient()
                async with client:
                    await client.send_command("/start")

                mock_telethon_client.send_message.assert_called_once_with("@test_bot", "/start")

    async def test_sends_command_with_arguments(self):
        """send_command should send command with arguments as-is."""
        from telegram_qa_service.client import TelegramQAClient

        env = {
            "TELEGRAM_API_ID": "12345678",
            "TELEGRAM_API_HASH": "abcdef1234567890",
            "TELEGRAM_QA_BOT_USERNAME": "@test_bot",
        }
        mock_telethon_client = AsyncMock()
        mock_telethon_client.connect = AsyncMock()
        mock_telethon_client.disconnect = AsyncMock()
        mock_telethon_client.is_user_authorized = AsyncMock(return_value=True)
        mock_telethon_client.send_message = AsyncMock()

        with patch.dict(os.environ, env, clear=True):
            with patch(
                "telegram_qa_service.client.TelegramClient",
                return_value=mock_telethon_client,
            ):
                client = TelegramQAClient()
                async with client:
                    await client.send_command("/search min_salary=5000")

                mock_telethon_client.send_message.assert_called_once_with(
                    "@test_bot", "/search min_salary=5000"
                )


class TestTelegramQAClientWaitForResponse:
    """Tests for TelegramQAClient.wait_for_response method."""

    async def test_returns_response_text_from_bot(self):
        """wait_for_response should return text from bot response message."""
        from telegram_qa_service.client import TelegramQAClient

        env = {
            "TELEGRAM_API_ID": "12345678",
            "TELEGRAM_API_HASH": "abcdef1234567890",
            "TELEGRAM_QA_BOT_USERNAME": "@test_bot",
        }
        mock_message = MagicMock()
        mock_message.text = "Welcome to Job Agent Bot!"

        mock_telethon_client = AsyncMock()
        mock_telethon_client.connect = AsyncMock()
        mock_telethon_client.disconnect = AsyncMock()
        mock_telethon_client.is_user_authorized = AsyncMock(return_value=True)

        # Mock get_entity to return bot entity
        mock_bot_entity = MagicMock()
        mock_bot_entity.id = 999
        mock_telethon_client.get_entity = AsyncMock(return_value=mock_bot_entity)

        # Set up conversation mock to return message
        async def mock_get_response(*args, **kwargs):
            return mock_message

        mock_telethon_client.get_messages = AsyncMock(return_value=[mock_message])

        with patch.dict(os.environ, env, clear=True):
            with patch(
                "telegram_qa_service.client.TelegramClient",
                return_value=mock_telethon_client,
            ):
                client = TelegramQAClient()
                async with client:
                    # Simulate setting up message listener
                    response = await client.wait_for_response()

                assert response == "Welcome to Job Agent Bot!"

    async def test_uses_custom_timeout_when_provided(self):
        """wait_for_response should use provided timeout over config default."""
        from telegram_qa_service.client import TelegramQAClient

        env = {
            "TELEGRAM_API_ID": "12345678",
            "TELEGRAM_API_HASH": "abcdef1234567890",
            "TELEGRAM_QA_BOT_USERNAME": "@test_bot",
            "TELEGRAM_QA_TIMEOUT": "30",
        }
        mock_message = MagicMock()
        mock_message.text = "Response"

        mock_telethon_client = AsyncMock()
        mock_telethon_client.connect = AsyncMock()
        mock_telethon_client.disconnect = AsyncMock()
        mock_telethon_client.is_user_authorized = AsyncMock(return_value=True)
        mock_telethon_client.get_messages = AsyncMock(return_value=[mock_message])

        mock_bot_entity = MagicMock()
        mock_bot_entity.id = 999
        mock_telethon_client.get_entity = AsyncMock(return_value=mock_bot_entity)

        with patch.dict(os.environ, env, clear=True):
            with patch(
                "telegram_qa_service.client.TelegramClient",
                return_value=mock_telethon_client,
            ):
                client = TelegramQAClient()
                async with client:
                    # The implementation should accept timeout_seconds parameter
                    response = await client.wait_for_response(timeout_seconds=60)

                assert response == "Response"

    async def test_raises_timeout_error_when_no_response(self):
        """wait_for_response should raise ResponseTimeoutError when timeout expires."""
        from telegram_qa_service.client import TelegramQAClient
        from telegram_qa_service.exceptions import ResponseTimeoutError

        env = {
            "TELEGRAM_API_ID": "12345678",
            "TELEGRAM_API_HASH": "abcdef1234567890",
            "TELEGRAM_QA_BOT_USERNAME": "@test_bot",
            "TELEGRAM_QA_TIMEOUT": "1",
        }
        mock_telethon_client = AsyncMock()
        mock_telethon_client.connect = AsyncMock()
        mock_telethon_client.disconnect = AsyncMock()
        mock_telethon_client.is_user_authorized = AsyncMock(return_value=True)

        # Simulate timeout by returning empty messages repeatedly
        mock_telethon_client.get_messages = AsyncMock(return_value=[])

        mock_bot_entity = MagicMock()
        mock_bot_entity.id = 999
        mock_telethon_client.get_entity = AsyncMock(return_value=mock_bot_entity)

        with patch.dict(os.environ, env, clear=True):
            with patch(
                "telegram_qa_service.client.TelegramClient",
                return_value=mock_telethon_client,
            ):
                client = TelegramQAClient()
                async with client:
                    with pytest.raises(ResponseTimeoutError) as exc_info:
                        await client.wait_for_response(timeout_seconds=0.1)

                assert "timeout" in str(exc_info.value).lower()

    async def test_filters_messages_to_only_target_bot(self):
        """wait_for_response should only return messages from the target bot."""
        from telegram_qa_service.client import TelegramQAClient

        env = {
            "TELEGRAM_API_ID": "12345678",
            "TELEGRAM_API_HASH": "abcdef1234567890",
            "TELEGRAM_QA_BOT_USERNAME": "@target_bot",
        }
        # Create mock messages from different senders
        bot_message = MagicMock()
        bot_message.text = "Bot response"
        bot_message.sender_id = 999  # Target bot ID

        other_message = MagicMock()
        other_message.text = "Other message"
        other_message.sender_id = 888  # Different user

        mock_telethon_client = AsyncMock()
        mock_telethon_client.connect = AsyncMock()
        mock_telethon_client.disconnect = AsyncMock()
        mock_telethon_client.is_user_authorized = AsyncMock(return_value=True)

        # get_entity returns bot with id 999
        mock_bot_entity = MagicMock()
        mock_bot_entity.id = 999
        mock_telethon_client.get_entity = AsyncMock(return_value=mock_bot_entity)

        # Messages include both bot and other user messages
        mock_telethon_client.get_messages = AsyncMock(return_value=[other_message, bot_message])

        with patch.dict(os.environ, env, clear=True):
            with patch(
                "telegram_qa_service.client.TelegramClient",
                return_value=mock_telethon_client,
            ):
                client = TelegramQAClient()
                async with client:
                    response = await client.wait_for_response()

                # Should return message from bot, not other user
                assert response == "Bot response"


class TestTelegramQAClientSendAndWait:
    """Tests for TelegramQAClient.send_and_wait convenience method."""

    async def test_sends_command_and_returns_response(self):
        """send_and_wait should send command and return bot response."""
        from telegram_qa_service.client import TelegramQAClient

        env = {
            "TELEGRAM_API_ID": "12345678",
            "TELEGRAM_API_HASH": "abcdef1234567890",
            "TELEGRAM_QA_BOT_USERNAME": "@test_bot",
        }
        # First call returns old message (ID=1), second call returns new response (ID=2)
        old_message = MagicMock()
        old_message.id = 1
        old_message.text = "Old message"
        old_message.sender_id = 999

        new_message = MagicMock()
        new_message.id = 2
        new_message.text = "Help text here"
        new_message.sender_id = 999

        mock_telethon_client = AsyncMock()
        mock_telethon_client.connect = AsyncMock()
        mock_telethon_client.disconnect = AsyncMock()
        mock_telethon_client.is_user_authorized = AsyncMock(return_value=True)
        mock_telethon_client.send_message = AsyncMock()
        # First call gets last message ID, subsequent calls return new message
        mock_telethon_client.get_messages = AsyncMock(side_effect=[[old_message], [new_message]])

        mock_bot_entity = MagicMock()
        mock_bot_entity.id = 999
        mock_telethon_client.get_entity = AsyncMock(return_value=mock_bot_entity)

        with patch.dict(os.environ, env, clear=True):
            with patch(
                "telegram_qa_service.client.TelegramClient",
                return_value=mock_telethon_client,
            ):
                client = TelegramQAClient()
                async with client:
                    response = await client.send_and_wait("/help")

                mock_telethon_client.send_message.assert_called_once_with("@test_bot", "/help")
                assert response == "Help text here"

    async def test_passes_timeout_to_wait_for_response(self):
        """send_and_wait should pass timeout_seconds to wait_for_response."""
        from telegram_qa_service.client import TelegramQAClient

        env = {
            "TELEGRAM_API_ID": "12345678",
            "TELEGRAM_API_HASH": "abcdef1234567890",
            "TELEGRAM_QA_BOT_USERNAME": "@test_bot",
        }
        # First call returns old message (ID=10), second call returns new response (ID=11)
        old_message = MagicMock()
        old_message.id = 10
        old_message.text = "Old"
        old_message.sender_id = 999

        new_message = MagicMock()
        new_message.id = 11
        new_message.text = "Response"
        new_message.sender_id = 999

        mock_telethon_client = AsyncMock()
        mock_telethon_client.connect = AsyncMock()
        mock_telethon_client.disconnect = AsyncMock()
        mock_telethon_client.is_user_authorized = AsyncMock(return_value=True)
        mock_telethon_client.send_message = AsyncMock()
        mock_telethon_client.get_messages = AsyncMock(side_effect=[[old_message], [new_message]])

        mock_bot_entity = MagicMock()
        mock_bot_entity.id = 999
        mock_telethon_client.get_entity = AsyncMock(return_value=mock_bot_entity)

        with patch.dict(os.environ, env, clear=True):
            with patch(
                "telegram_qa_service.client.TelegramClient",
                return_value=mock_telethon_client,
            ):
                client = TelegramQAClient()
                async with client:
                    # Providing custom timeout
                    response = await client.send_and_wait("/start", timeout_seconds=120)

                assert response == "Response"
