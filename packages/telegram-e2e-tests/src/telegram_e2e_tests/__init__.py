"""Telegram QA Service - E2E testing for Telegram bots using Telethon.

This package provides a client for testing Telegram bots by acting as a real
Telegram user. It allows sending commands to bots and verifying their responses.

Example usage:
    from telegram_e2e_tests import TelegramQAClient

    async with TelegramQAClient() as client:
        response = await client.send_and_wait("/start")
        assert "Welcome" in response
"""

from telegram_e2e_tests.client import TelegramQAClient
from telegram_e2e_tests.config import QAConfig, load_config
from telegram_e2e_tests.exceptions import (
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
