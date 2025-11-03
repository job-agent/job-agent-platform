"""Jobs Repository Package - PostgreSQL database operations for job listings."""

# Database
from jobs_repository.database import (
    Base,
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

# Models
from jobs_repository.models import Job, Company, Location, Category, Industry

# Repository
from jobs_repository.repository import JobRepository

# Mapper
from jobs_repository.mapper import JobMapper

# Schemas
from jobs_repository.schemas import JobCreate

# Exceptions
from jobs_repository.exceptions import (
    JobRepositoryError,
    JobNotFoundError,
    JobAlreadyExistsError,
    DatabaseConnectionError,
    ValidationError,
    TransactionError,
)

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
    "Job",
    "Company",
    "Location",
    "Category",
    "Industry",
    # Repository
    "JobRepository",
    # Mapper
    "JobMapper",
    # Schemas
    "JobCreate",
    # Exceptions
    "JobRepositoryError",
    "JobNotFoundError",
    "JobAlreadyExistsError",
    "DatabaseConnectionError",
    "ValidationError",
    "TransactionError",
]
