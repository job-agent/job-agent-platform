"""Database module - connection and session management."""

from jobs_repository.database.base import Base
from jobs_repository.database.config import DatabaseConfig, get_database_config
from jobs_repository.database.connection import get_engine, reset_engine
from jobs_repository.database.session import (
    get_db_session,
    get_session_factory,
    transaction,
)
from jobs_repository.database.lifecycle import init_db, drop_all_tables

__all__ = [
    # Base
    "Base",
    # Config
    "DatabaseConfig",
    "get_database_config",
    # Connection
    "get_engine",
    "reset_engine",
    # Session
    "get_db_session",
    "get_session_factory",
    "transaction",
    # Lifecycle
    "init_db",
    "drop_all_tables",
]
