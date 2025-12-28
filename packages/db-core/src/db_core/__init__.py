"""db-core: Shared database infrastructure for job-agent-platform repositories.

This package provides common database utilities:
- Configuration: DatabaseConfig, get_database_config
- Connection: get_engine, reset_engine
- Session: get_session_factory, reset_session_factory, get_db_session, transaction
- Lifecycle: init_db, drop_all_tables
- Base: SQLAlchemy declarative Base
- Exceptions: DatabaseError, DatabaseConnectionError, TransactionError
- Repository: BaseRepository
"""

# Exceptions (no dependencies)
from db_core.exceptions import (
    DatabaseError,
    DatabaseConnectionError,
    TransactionError,
)

# Configuration
from db_core.config import (
    DatabaseConfig,
    get_database_config,
)

# Base
from db_core.base import Base

# Connection
from db_core.connection import (
    get_engine,
    reset_engine,
)

# Session
from db_core.session import (
    get_session_factory,
    reset_session_factory,
    get_db_session,
    transaction,
)

# Lifecycle
from db_core.lifecycle import (
    init_db,
    drop_all_tables,
)

# Repository
from db_core.repository import BaseRepository

# Submodules for direct import
from db_core import (
    config,
    connection,
    session,
    lifecycle,
    base,
    exceptions,
    repository,
)

__all__ = [
    # Exceptions
    "DatabaseError",
    "DatabaseConnectionError",
    "TransactionError",
    # Configuration
    "DatabaseConfig",
    "get_database_config",
    # Base
    "Base",
    # Connection
    "get_engine",
    "reset_engine",
    # Session
    "get_session_factory",
    "reset_session_factory",
    "get_db_session",
    "transaction",
    # Lifecycle
    "init_db",
    "drop_all_tables",
    # Repository
    "BaseRepository",
    # Submodules
    "config",
    "connection",
    "session",
    "lifecycle",
    "base",
    "exceptions",
    "repository",
]
