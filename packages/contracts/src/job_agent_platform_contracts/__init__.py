"""Shared contracts and data models for job-agent platform."""

from job_agent_platform_contracts.job_repository import (
    IJobRepository,
    JobAgentError,
    RepositoryError,
    JobAlreadyExistsError,
    JobNotFoundError,
    ValidationError,
    TransactionError,
)
from job_agent_platform_contracts.cv_repository import ICVRepository

__version__ = "0.1.0"

__all__ = [
    "IJobRepository",
    "ICVRepository",
    "JobAgentError",
    "RepositoryError",
    "JobAlreadyExistsError",
    "JobNotFoundError",
    "ValidationError",
    "TransactionError",
]
