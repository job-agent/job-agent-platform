"""Shared job-agent-platform-contracts and data models for job-agent platform."""

from job_agent_platform_contracts.job_repository import (
    IJobRepository,
    JobAgentError,
    RepositoryError,
    JobAlreadyExistsError,
    JobNotFoundError,
    ValidationError,
    TransactionError,
    DatabaseConnectionError,
)
from job_agent_platform_contracts.cv_repository import ICVRepository
from job_agent_platform_contracts.core import JobProcessingResult, PipelineSummary
from job_agent_platform_contracts.core.orchestrator import IJobAgentOrchestrator
from job_agent_platform_contracts.essay_repository import IEssayRepository

__version__ = "0.1.0"

__all__ = [
    "IJobRepository",
    "ICVRepository",
    "IEssayRepository",
    "IJobAgentOrchestrator",
    "JobProcessingResult",
    "PipelineSummary",
    "JobAgentError",
    "RepositoryError",
    "JobAlreadyExistsError",
    "JobNotFoundError",
    "ValidationError",
    "TransactionError",
    "DatabaseConnectionError",
]
