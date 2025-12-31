"""Configuration loading for the Telegram QA service."""

import os
from dataclasses import dataclass

from telegram_qa_service.exceptions import ConfigurationError


@dataclass(frozen=True)
class QAConfig:
    """Configuration for Telegram QA client.

    Attributes:
        api_id: Telegram API ID from my.telegram.org
        api_hash: Telegram API hash from my.telegram.org
        bot_username: Username of the bot to test (e.g., @job_agent_bot)
        session_path: Path to store Telethon session file
        timeout: Default timeout in seconds for waiting on bot responses
    """

    api_id: int
    api_hash: str
    bot_username: str
    session_path: str
    timeout: int


def load_config() -> QAConfig:
    """Load QA configuration from environment variables.

    Required environment variables:
        - TELEGRAM_API_ID: Telegram API ID (integer)
        - TELEGRAM_API_HASH: Telegram API hash
        - TELEGRAM_QA_BOT_USERNAME: Bot username to test

    Optional environment variables:
        - TELEGRAM_QA_SESSION_PATH: Session file path (default: telegram_qa.session)
        - TELEGRAM_QA_TIMEOUT: Response timeout in seconds (default: 30)

    Returns:
        QAConfig with loaded values

    Raises:
        ConfigurationError: If required variables are missing or invalid
    """
    api_id_str = os.getenv("TELEGRAM_API_ID")
    if not api_id_str:
        raise ConfigurationError(
            "TELEGRAM_API_ID environment variable is required. Get this from my.telegram.org"
        )

    try:
        api_id = int(api_id_str)
    except ValueError:
        raise ConfigurationError(f"TELEGRAM_API_ID must be a valid integer, got: {api_id_str}")

    api_hash = os.getenv("TELEGRAM_API_HASH")
    if not api_hash:
        raise ConfigurationError(
            "TELEGRAM_API_HASH environment variable is required. Get this from my.telegram.org"
        )

    bot_username = os.getenv("TELEGRAM_QA_BOT_USERNAME")
    if not bot_username:
        raise ConfigurationError(
            "TELEGRAM_QA_BOT_USERNAME environment variable is required. "
            "This is the username of the bot to test (e.g., @job_agent_bot)"
        )

    session_path = os.getenv("TELEGRAM_QA_SESSION_PATH", "telegram_qa.session")

    timeout_str = os.getenv("TELEGRAM_QA_TIMEOUT", "30")
    try:
        timeout = int(timeout_str)
    except ValueError:
        raise ConfigurationError(f"TELEGRAM_QA_TIMEOUT must be a valid integer, got: {timeout_str}")

    return QAConfig(
        api_id=api_id,
        api_hash=api_hash,
        bot_username=bot_username,
        session_path=session_path,
        timeout=timeout,
    )
