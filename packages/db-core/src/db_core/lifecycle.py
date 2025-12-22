"""Database lifecycle management.

This module provides database lifecycle functions:
- init_db: Initialize database by creating all tables
- drop_all_tables: Drop all tables from the database
"""

from typing import Any, Optional

from sqlalchemy import Engine

from db_core.base import Base
from db_core.connection import get_engine
from db_core.exceptions import DatabaseConnectionError


def init_db(base: Optional[Any] = None, engine: Optional[Engine] = None) -> None:
    """Initialize the database by creating all tables.

    This should be called once when setting up the database.
    For production, use Alembic migrations instead.

    Args:
        base: SQLAlchemy declarative base (defaults to db_core.Base)
        engine: SQLAlchemy engine (defaults to get_engine())

    Raises:
        DatabaseConnectionError: If initialization fails
    """
    try:
        if base is None:
            base = Base
        if engine is None:
            engine = get_engine()
        base.metadata.create_all(bind=engine)
    except Exception as e:
        raise DatabaseConnectionError(f"Failed to initialize database: {e}") from e


def drop_all_tables(base: Optional[Any] = None, engine: Optional[Engine] = None) -> None:
    """Drop all tables from the database.

    WARNING: This will delete all data. Use with caution!
    Only intended for development/testing.

    Args:
        base: SQLAlchemy declarative base (defaults to db_core.Base)
        engine: SQLAlchemy engine (defaults to get_engine())

    Raises:
        DatabaseConnectionError: If operation fails
    """
    try:
        if base is None:
            base = Base
        if engine is None:
            engine = get_engine()
        base.metadata.drop_all(bind=engine)
    except Exception as e:
        raise DatabaseConnectionError(f"Failed to drop tables: {e}") from e
