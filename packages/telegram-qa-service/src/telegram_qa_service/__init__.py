"""Telegram QA Service - E2E testing for Telegram bots using Telethon.

This package provides a client for testing Telegram bots by acting as a real
Telegram user. It allows sending commands to bots and verifying their responses.

Example usage:
    from telegram_qa_service import TelegramQAClient

    async with TelegramQAClient() as client:
        response = await client.send_and_wait("/start")
        assert "Welcome" in response
"""

from telegram_qa_service.client import TelegramQAClient
from telegram_qa_service.config import QAConfig, load_config
from telegram_qa_service.exceptions import (
    ConfigurationError,
    ConnectionError,
    ResponseTimeoutError,
    TelegramQAError,
)

__all__ = [
    "TelegramQAClient",
    "QAConfig",
    "load_config",
    "TelegramQAError",
    "ConfigurationError",
    "ConnectionError",
    "ResponseTimeoutError",
]
