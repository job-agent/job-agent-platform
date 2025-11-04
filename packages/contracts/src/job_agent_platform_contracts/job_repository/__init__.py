"""Job repository contracts and exceptions."""

from job_agent_platform_contracts.job_repository.repository import IJobRepository
from job_agent_platform_contracts.job_repository.exceptions import (
    JobAgentError,
    RepositoryError,
    JobAlreadyExistsError,
    JobNotFoundError,
    ValidationError,
    TransactionError,
)

__all__ = [
    "IJobRepository",
    "JobAgentError",
    "RepositoryError",
    "JobAlreadyExistsError",
    "JobNotFoundError",
    "ValidationError",
    "TransactionError",
]
