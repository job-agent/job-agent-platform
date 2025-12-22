"""Database connection management.

This module provides thread-safe database engine management:
- get_engine: Get or create singleton SQLAlchemy engine
- reset_engine: Dispose and reset the global engine
"""

import threading
from typing import Optional

from sqlalchemy import create_engine, Engine, text

from db_core.config import get_database_config
from db_core.exceptions import DatabaseConnectionError


_engine: Optional[Engine] = None
_engine_lock = threading.Lock()


def get_engine() -> Engine:
    """Get or create the SQLAlchemy engine.

    Creates a singleton engine instance with thread-safe initialization.
    The engine is configured with pool_pre_ping for connection validation
    and verifies connectivity with SELECT 1.

    Returns:
        SQLAlchemy engine instance

    Raises:
        DatabaseConnectionError: If connection fails or verification fails
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
    """Reset the global engine.

    Disposes of the existing engine connection pool and resets the global
    engine to None. Useful for testing or when configuration changes.
    """
    global _engine

    with _engine_lock:
        if _engine is not None:
            _engine.dispose()
            _engine = None
