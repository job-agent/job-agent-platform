"""Essay repository package for PostgreSQL database operations."""

from db_core import (
    DatabaseConfig,
    get_database_config,
    get_engine,
    reset_engine,
    get_db_session,
    get_session_factory,
    transaction,
    init_db,
    drop_all_tables,
)
from essay_repository.models.base import Base
from essay_repository.models import Essay
from essay_repository.repository import EssayRepository
from essay_repository.container import get_essay_repository

__version__ = "0.1.0"

__all__ = [
    # Database
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
    # Models
    "Essay",
    # Repository
    "EssayRepository",
    # Container
    "get_essay_repository",
]
