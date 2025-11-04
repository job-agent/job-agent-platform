"""Jobs Repository Package - PostgreSQL database operations for job listings."""

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

from jobs_repository.models import Job, Company, Location, Category, Industry

from jobs_repository.repository import JobRepository

from jobs_repository.mapper import JobMapper

from job_agent_platform_contracts.job_repository.schemas import JobCreate

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
    "Job",
    "Company",
    "Location",
    "Category",
    "Industry",
    "JobRepository",
    "JobMapper",
    "JobCreate",
    "JobRepositoryError",
    "JobNotFoundError",
    "JobAlreadyExistsError",
    "DatabaseConnectionError",
    "ValidationError",
    "TransactionError",
]
