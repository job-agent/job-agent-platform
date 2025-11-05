"""Database-related exceptions."""

from .exceptions import JobRepositoryError


class DatabaseConnectionError(JobRepositoryError):
    """Raised when database connection fails."""

    pass


class TransactionError(JobRepositoryError):
    """Raised when a database transaction fails."""

    pass
