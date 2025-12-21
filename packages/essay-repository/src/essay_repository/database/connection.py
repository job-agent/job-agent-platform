"""Database connection management."""

import threading
from typing import Optional
from sqlalchemy import create_engine, Engine, text

from essay_repository.database.config import get_database_config
from job_agent_platform_contracts.job_repository.exceptions import DatabaseConnectionError


_engine: Optional[Engine] = None
_engine_lock = threading.Lock()


def get_engine() -> Engine:
    """
    Get or create the SQLAlchemy engine.

    Returns:
        SQLAlchemy engine instance

    Raises:
        DatabaseConnectionError: If connection fails
    """
    global _engine

    if _engine is not None:
        return _engine

    with _engine_lock:
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

                with _engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
            except Exception as e:
                raise DatabaseConnectionError(f"Failed to connect to database: {e}") from e

    return _engine


def reset_engine() -> None:
    """
    Reset the global engine.

    Useful for testing or when configuration changes.
    """
    global _engine

    with _engine_lock:
        if _engine is not None:
            _engine.dispose()
            _engine = None
