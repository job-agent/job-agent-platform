"""Dependency injection container for jobs repository services."""

from dependency_injector import containers, providers
from job_agent_platform_contracts import IJobRepository

from jobs_repository.database import get_session_factory
from jobs_repository.repository.job_repository import JobRepository


class JobsRepositoryContainer(containers.DeclarativeContainer):
    """Configure dependency providers for the jobs repository package."""

    config = providers.Configuration()

    session_factory = providers.Singleton(get_session_factory)

    job_repository = providers.Factory(
        JobRepository,
        session_factory=session_factory,
    )


container = JobsRepositoryContainer()


def get_job_repository() -> IJobRepository:
    """Provide a JobRepository instance with managed session lifecycle."""

    return container.job_repository()
