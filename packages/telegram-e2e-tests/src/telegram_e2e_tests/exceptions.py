"""Custom exceptions for the Telegram QA service."""


class TelegramQAError(Exception):
    """Base exception for all Telegram QA service errors."""


class ConfigurationError(TelegramQAError):
    """Raised when configuration is missing or invalid."""


class ConnectionError(TelegramQAError):
    """Raised when connection to Telegram fails."""


class ResponseTimeoutError(TelegramQAError):
    """Raised when waiting for bot response times out."""
