"""Database module - connection and session management."""

from essay_repository.database.base import Base
from essay_repository.database.config import DatabaseConfig, get_database_config
from essay_repository.database.connection import get_engine, reset_engine
from essay_repository.database.session import (
    get_db_session,
    get_session_factory,
    transaction,
)
from essay_repository.database.lifecycle import init_db, drop_all_tables

__all__ = [
    "Base",
    "DatabaseConfig",
    "get_database_config",
    "get_engine",
    "reset_engine",
    "get_db_session",
    "get_session_factory",
    "transaction",
    "init_db",
    "drop_all_tables",
]
