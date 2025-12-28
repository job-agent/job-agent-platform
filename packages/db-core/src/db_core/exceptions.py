"""Database exception classes.

This module defines the exception hierarchy for database-related errors:
- DatabaseError: Base class for all database exceptions
- DatabaseConnectionError: Raised when database connection fails
- TransactionError: Raised when database transaction fails
"""


class DatabaseError(Exception):
    """Base exception for all database-related errors.

    All database exceptions inherit from this class, allowing consumers
    to catch all database errors with a single except clause.
    """

    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails.

    This exception is raised when:
    - Engine creation fails
    - Connection verification fails (SELECT 1)
    - Database is unreachable
    """

    pass


class TransactionError(DatabaseError):
    """Raised when database transaction fails.

    This exception is raised when:
    - Session operations fail
    - Transaction commit fails
    - Transaction rollback is triggered
    """

    pass
