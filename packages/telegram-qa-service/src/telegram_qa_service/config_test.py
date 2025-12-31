"""Tests for telegram QA service configuration loading."""

import os
from unittest.mock import patch

import pytest


class TestLoadConfig:
    """Tests for load_config function."""

    def test_loads_all_config_from_environment(self):
        """Config should load all fields from environment variables."""
        from telegram_qa_service.config import load_config

        env = {
            "TELEGRAM_API_ID": "12345678",
            "TELEGRAM_API_HASH": "abcdef1234567890",
            "TELEGRAM_QA_BOT_USERNAME": "@job_agent_bot",
            "TELEGRAM_QA_SESSION_PATH": "/custom/path/session.session",
            "TELEGRAM_QA_TIMEOUT": "60",
        }
        with patch.dict(os.environ, env, clear=True):
            config = load_config()

        assert config.api_id == 12345678
        assert config.api_hash == "abcdef1234567890"
        assert config.bot_username == "@job_agent_bot"
        assert config.session_path == "/custom/path/session.session"
        assert config.timeout == 60


class TestLoadConfigMissingRequired:
    """Tests for load_config error handling when required variables are missing."""

    def test_raises_error_when_api_id_missing(self):
        """Config should raise ConfigurationError when TELEGRAM_API_ID is missing."""
        from telegram_qa_service.config import load_config
        from telegram_qa_service.exceptions import ConfigurationError

        env = {
            "TELEGRAM_API_HASH": "abcdef1234567890",
            "TELEGRAM_QA_BOT_USERNAME": "@test_bot",
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ConfigurationError) as exc_info:
                load_config()

        assert "TELEGRAM_API_ID" in str(exc_info.value)

    def test_raises_error_when_api_hash_missing(self):
        """Config should raise ConfigurationError when TELEGRAM_API_HASH is missing."""
        from telegram_qa_service.config import load_config
        from telegram_qa_service.exceptions import ConfigurationError

        env = {
            "TELEGRAM_API_ID": "12345678",
            "TELEGRAM_QA_BOT_USERNAME": "@test_bot",
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ConfigurationError) as exc_info:
                load_config()

        assert "TELEGRAM_API_HASH" in str(exc_info.value)

    def test_raises_error_when_bot_username_missing(self):
        """Config should raise ConfigurationError when TELEGRAM_QA_BOT_USERNAME is missing."""
        from telegram_qa_service.config import load_config
        from telegram_qa_service.exceptions import ConfigurationError

        env = {
            "TELEGRAM_API_ID": "12345678",
            "TELEGRAM_API_HASH": "abcdef1234567890",
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ConfigurationError) as exc_info:
                load_config()

        assert "TELEGRAM_QA_BOT_USERNAME" in str(exc_info.value)


class TestLoadConfigInvalidValues:
    """Tests for load_config error handling with invalid values."""

    def test_raises_error_when_api_id_not_numeric(self):
        """Config should raise ConfigurationError when TELEGRAM_API_ID is not a valid integer."""
        from telegram_qa_service.config import load_config
        from telegram_qa_service.exceptions import ConfigurationError

        env = {
            "TELEGRAM_API_ID": "not_a_number",
            "TELEGRAM_API_HASH": "abcdef1234567890",
            "TELEGRAM_QA_BOT_USERNAME": "@test_bot",
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ConfigurationError) as exc_info:
                load_config()

        assert "TELEGRAM_API_ID" in str(exc_info.value)

    def test_raises_error_when_timeout_not_numeric(self):
        """Config should raise ConfigurationError when TELEGRAM_QA_TIMEOUT is not a valid integer."""
        from telegram_qa_service.config import load_config
        from telegram_qa_service.exceptions import ConfigurationError

        env = {
            "TELEGRAM_API_ID": "12345678",
            "TELEGRAM_API_HASH": "abcdef1234567890",
            "TELEGRAM_QA_BOT_USERNAME": "@test_bot",
            "TELEGRAM_QA_TIMEOUT": "not_a_number",
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ConfigurationError) as exc_info:
                load_config()

        assert "TELEGRAM_QA_TIMEOUT" in str(exc_info.value)


class TestQAConfig:
    """Tests for QAConfig dataclass."""

    def test_config_is_immutable(self):
        """QAConfig should be immutable (frozen dataclass)."""
        from telegram_qa_service.config import QAConfig

        config = QAConfig(
            api_id=12345678,
            api_hash="abcdef",
            bot_username="@bot",
            session_path="session.session",
            timeout=30,
        )

        with pytest.raises(AttributeError):
            config.api_id = 99999999  # type: ignore
