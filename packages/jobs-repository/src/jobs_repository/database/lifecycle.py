"""Database lifecycle management."""

from jobs_repository.database.base import Base
from jobs_repository.database.connection import get_engine
from jobs_repository.exceptions import DatabaseConnectionError


def init_db() -> None:
    """
    Initialize the database by creating all tables.

    This should be called once when setting up the database.
    For production, use Alembic migrations instead.

    Raises:
        DatabaseConnectionError: If initialization fails
    """
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        raise DatabaseConnectionError(f"Failed to initialize database: {e}") from e


def drop_all_tables() -> None:
    """
    Drop all tables from the database.

    WARNING: This will delete all data. Use with caution!
    Only intended for development/testing.

    Raises:
        DatabaseConnectionError: If operation fails
    """
    try:
        engine = get_engine()
        Base.metadata.drop_all(bind=engine)
    except Exception as e:
        raise DatabaseConnectionError(f"Failed to drop tables: {e}") from e
