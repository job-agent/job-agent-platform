"""Jobs Repository Package - PostgreSQL database operations for job listings."""

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

from jobs_repository.models.base import Base
from jobs_repository.models import Job, Company, Location, Category, Industry

from jobs_repository.repository import JobRepository

from jobs_repository.mapper import JobMapper

from jobs_repository.container import get_job_repository

from job_agent_platform_contracts.job_repository.schemas import JobCreate

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
    "get_job_repository",
    "JobCreate",
]
