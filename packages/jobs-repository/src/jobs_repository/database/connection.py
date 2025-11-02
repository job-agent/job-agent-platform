"""Database connection management."""

from typing import Optional
from sqlalchemy import create_engine, Engine

from jobs_repository.database.config import get_database_config
from jobs_repository.exceptions import DatabaseConnectionError

# Global engine (initialized lazily)
_engine: Optional[Engine] = None


def get_engine() -> Engine:
    """
    Get or create the SQLAlchemy engine.

    Returns:
        SQLAlchemy engine instance

    Raises:
        DatabaseConnectionError: If connection fails
    """
    global _engine

    if _engine is None:
        try:
            config = get_database_config()
            _engine = create_engine(
                config.url,
                pool_pre_ping=True,
                pool_size=config.pool_size,
                max_overflow=config.max_overflow,
                echo=config.echo,
            )
            # Test connection
            with _engine.connect() as conn:
                conn.execute("SELECT 1")
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to connect to database: {e}") from e

    return _engine


def reset_engine() -> None:
    """
    Reset the global engine.

    Useful for testing or when configuration changes.
    """
    global _engine

    if _engine is not None:
        _engine.dispose()
        _engine = None
