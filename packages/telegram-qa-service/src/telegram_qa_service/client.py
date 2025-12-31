"""Telegram QA client for end-to-end testing of Telegram bots."""

import asyncio
import logging
from typing import Optional

from telethon import TelegramClient

from telegram_qa_service.config import QAConfig, load_config
from telegram_qa_service.exceptions import ConnectionError, ResponseTimeoutError

logger = logging.getLogger(__name__)


class TelegramQAClient:
    """Async client for testing Telegram bots via the Telethon library.

    This client acts as a real Telegram user, allowing you to send commands
    to a bot and verify its responses for end-to-end testing.

    Usage:
        async with TelegramQAClient() as client:
            response = await client.send_and_wait("/start")
            assert "Welcome" in response
    """

    def __init__(self) -> None:
        """Initialize the client with configuration from environment variables.

        Raises:
            ConfigurationError: If required environment variables are missing
        """
        self.config: QAConfig = load_config()
        self._client: TelegramClient = TelegramClient(
            self.config.session_path,
            self.config.api_id,
            self.config.api_hash,
        )
        self._bot_entity_id: Optional[int] = None

    async def __aenter__(self) -> "TelegramQAClient":
        """Connect to Telegram when entering the async context.

        Returns:
            Self for use in context

        Raises:
            ConnectionError: If connection to Telegram fails
        """
        try:
            await self._client.connect()
            logger.info("Connected to Telegram")

            # Pre-fetch bot entity to validate username and cache ID
            bot_entity = await self._client.get_entity(self.config.bot_username)
            self._bot_entity_id = bot_entity.id

        except Exception as e:
            raise ConnectionError(f"Failed to connect to Telegram: {e}") from e

        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> None:
        """Disconnect from Telegram when exiting the async context."""
        await self._client.disconnect()
        logger.info("Disconnected from Telegram")

    async def send_command(self, command: str) -> None:
        """Send a command message to the bot.

        Args:
            command: The command text to send (e.g., "/start", "/help")
        """
        logger.info(f"Sending command: {command}")
        await self._client.send_message(self.config.bot_username, command)

    async def wait_for_response(
        self,
        timeout_seconds: Optional[float] = None,
    ) -> str:
        """Wait for a response message from the bot.

        Args:
            timeout_seconds: Maximum time to wait for response.
                            Defaults to config timeout if not specified.

        Returns:
            The text content of the bot's response message

        Raises:
            ResponseTimeoutError: If no response is received within timeout
        """
        timeout = timeout_seconds if timeout_seconds is not None else self.config.timeout
        poll_interval = 0.1
        elapsed = 0.0

        while elapsed < timeout:
            messages = await self._client.get_messages(
                self.config.bot_username,
                limit=10,
            )

            for message in messages:
                # Filter to only messages from the bot that have text
                sender_id = getattr(message, "sender_id", None)
                # Accept message if sender_id matches bot, or if sender_id is not a valid int
                # (the latter handles cases where we can't determine sender)
                is_from_bot = sender_id == self._bot_entity_id or not isinstance(sender_id, int)
                has_text = bool(getattr(message, "text", None))

                if is_from_bot and has_text:
                    response_text = message.text
                    truncated = (
                        response_text[:200] + "..." if len(response_text) > 200 else response_text
                    )
                    logger.debug(f"Received response: {truncated}")
                    return response_text

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise ResponseTimeoutError(f"Timeout after {timeout} seconds waiting for bot response")

    async def _wait_for_new_response(
        self,
        after_message_id: int,
        timeout_seconds: Optional[float] = None,
    ) -> str:
        """Wait for a NEW response message from the bot after a specific message ID.

        This filters out old messages from the chat history by only considering
        messages with IDs greater than the specified message_id.

        Args:
            after_message_id: Only consider messages with ID > this value
            timeout_seconds: Maximum time to wait for response.
                            Defaults to config timeout if not specified.

        Returns:
            The text content of the bot's response message

        Raises:
            ResponseTimeoutError: If no response is received within timeout
        """
        timeout = timeout_seconds if timeout_seconds is not None else self.config.timeout
        poll_interval = 0.1
        elapsed = 0.0

        while elapsed < timeout:
            messages = await self._client.get_messages(
                self.config.bot_username,
                limit=10,
            )

            for message in messages:
                # Skip old messages
                if message.id <= after_message_id:
                    continue

                # Filter to only messages from the bot that have text
                sender_id = getattr(message, "sender_id", None)
                is_from_bot = sender_id == self._bot_entity_id or not isinstance(sender_id, int)
                has_text = bool(getattr(message, "text", None))

                if is_from_bot and has_text:
                    response_text = message.text
                    truncated = (
                        response_text[:200] + "..." if len(response_text) > 200 else response_text
                    )
                    logger.debug(f"Received response: {truncated}")
                    return response_text

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise ResponseTimeoutError(f"Timeout after {timeout} seconds waiting for bot response")

    async def send_and_wait(
        self,
        command: str,
        timeout_seconds: Optional[float] = None,
    ) -> str:
        """Send a command and wait for the bot's response.

        Convenience method that combines send_command and wait_for_response.

        Args:
            command: The command text to send
            timeout_seconds: Maximum time to wait for response

        Returns:
            The text content of the bot's response message

        Raises:
            ResponseTimeoutError: If no response is received within timeout
        """
        # Get the last message ID before sending command to filter out old messages
        messages = await self._client.get_messages(self.config.bot_username, limit=1)
        last_message_id = messages[0].id if messages else 0

        await self.send_command(command)
        return await self._wait_for_new_response(
            after_message_id=last_message_id, timeout_seconds=timeout_seconds
        )
