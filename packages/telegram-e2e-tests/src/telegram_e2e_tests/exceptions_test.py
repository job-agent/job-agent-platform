"""Tests for telegram QA service exception classes."""

import pytest


class TestTelegramQAError:
    """Tests for TelegramQAError base exception."""

    def test_is_base_exception_class(self):
        """TelegramQAError should be a base exception that other errors inherit from."""
        from telegram_e2e_tests.exceptions import TelegramQAError

        error = TelegramQAError("test error")

        assert isinstance(error, Exception)
        assert str(error) == "test error"

    def test_can_be_raised_and_caught(self):
        """TelegramQAError can be raised and caught."""
        from telegram_e2e_tests.exceptions import TelegramQAError

        with pytest.raises(TelegramQAError) as exc_info:
            raise TelegramQAError("base telegram qa error")

        assert "base telegram qa error" in str(exc_info.value)


class TestConfigurationError:
    """Tests for ConfigurationError exception."""

    def test_inherits_from_telegram_qa_error(self):
        """ConfigurationError should inherit from TelegramQAError."""
        from telegram_e2e_tests.exceptions import ConfigurationError, TelegramQAError

        error = ConfigurationError("missing api key")

        assert isinstance(error, TelegramQAError)
        assert isinstance(error, Exception)

    def test_can_be_raised_with_message(self):
        """ConfigurationError can be raised with a descriptive message."""
        from telegram_e2e_tests.exceptions import ConfigurationError

        with pytest.raises(ConfigurationError) as exc_info:
            raise ConfigurationError("TELEGRAM_API_ID environment variable is required")

        assert "TELEGRAM_API_ID" in str(exc_info.value)
        assert "required" in str(exc_info.value)

    def test_can_be_caught_as_telegram_qa_error(self):
        """ConfigurationError can be caught as TelegramQAError."""
        from telegram_e2e_tests.exceptions import ConfigurationError, TelegramQAError

        with pytest.raises(TelegramQAError):
            raise ConfigurationError("config error")


class TestConnectionError:
    """Tests for ConnectionError exception."""

    def test_inherits_from_telegram_qa_error(self):
        """ConnectionError should inherit from TelegramQAError."""
        from telegram_e2e_tests.exceptions import ConnectionError, TelegramQAError

        error = ConnectionError("failed to connect")

        assert isinstance(error, TelegramQAError)
        assert isinstance(error, Exception)

    def test_can_be_raised_with_message(self):
        """ConnectionError can be raised with a descriptive message."""
        from telegram_e2e_tests.exceptions import ConnectionError

        with pytest.raises(ConnectionError) as exc_info:
            raise ConnectionError("Failed to connect to Telegram: network unavailable")

        assert "Failed to connect to Telegram" in str(exc_info.value)
        assert "network unavailable" in str(exc_info.value)

    def test_can_be_caught_as_telegram_qa_error(self):
        """ConnectionError can be caught as TelegramQAError."""
        from telegram_e2e_tests.exceptions import ConnectionError, TelegramQAError

        with pytest.raises(TelegramQAError):
            raise ConnectionError("connection failed")

    def test_preserves_original_exception_chain(self):
        """ConnectionError preserves exception chain when raised from another error."""
        from telegram_e2e_tests.exceptions import ConnectionError

        original = Exception("original error")

        with pytest.raises(ConnectionError) as exc_info:
            try:
                raise original
            except Exception as e:
                raise ConnectionError(f"Wrapped: {e}") from e

        assert exc_info.value.__cause__ is original


class TestResponseTimeoutError:
    """Tests for ResponseTimeoutError exception."""

    def test_inherits_from_telegram_qa_error(self):
        """ResponseTimeoutError should inherit from TelegramQAError."""
        from telegram_e2e_tests.exceptions import ResponseTimeoutError, TelegramQAError

        error = ResponseTimeoutError("timeout waiting for response")

        assert isinstance(error, TelegramQAError)
        assert isinstance(error, Exception)

    def test_can_be_raised_with_message(self):
        """ResponseTimeoutError can be raised with a descriptive message."""
        from telegram_e2e_tests.exceptions import ResponseTimeoutError

        with pytest.raises(ResponseTimeoutError) as exc_info:
            raise ResponseTimeoutError(
                "Timeout after 30 seconds waiting for bot response to /start"
            )

        assert "Timeout" in str(exc_info.value)
        assert "30 seconds" in str(exc_info.value)
        assert "/start" in str(exc_info.value)

    def test_can_be_caught_as_telegram_qa_error(self):
        """ResponseTimeoutError can be caught as TelegramQAError."""
        from telegram_e2e_tests.exceptions import ResponseTimeoutError, TelegramQAError

        with pytest.raises(TelegramQAError):
            raise ResponseTimeoutError("timeout")


class TestExceptionHierarchy:
    """Tests for the exception class hierarchy."""

    def test_all_errors_share_common_base(self):
        """All error types share TelegramQAError as common base."""
        from telegram_e2e_tests.exceptions import (
            ConfigurationError,
            ConnectionError,
            ResponseTimeoutError,
            TelegramQAError,
        )

        config_error = ConfigurationError("config")
        conn_error = ConnectionError("conn")
        timeout_error = ResponseTimeoutError("timeout")

        assert isinstance(config_error, TelegramQAError)
        assert isinstance(conn_error, TelegramQAError)
        assert isinstance(timeout_error, TelegramQAError)
