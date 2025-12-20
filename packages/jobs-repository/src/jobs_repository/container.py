"""Dependency injection container for jobs repository services."""

from dependency_injector import containers, providers
from job_agent_platform_contracts import IJobRepository

from jobs_repository.database import get_session_factory
from jobs_repository.repository.job_repository import JobRepository
from jobs_repository.services import ReferenceDataService
from jobs_repository.mapper import JobMapper


class JobsRepositoryContainer(containers.DeclarativeContainer):
    """Configure dependency providers for the jobs repository package."""

    config = providers.Configuration()

    session_factory = providers.Singleton(get_session_factory)

    reference_data_service = providers.Singleton(ReferenceDataService)

    job_mapper = providers.Singleton(JobMapper)

    job_repository = providers.Factory(
        JobRepository,
        reference_data_service=reference_data_service,
        mapper=job_mapper,
        session_factory=session_factory,
    )


container = JobsRepositoryContainer()


def get_job_repository() -> IJobRepository:
    """Provide a JobRepository instance with managed session lifecycle."""
    repository = container.job_repository()
    if callable(repository) and not isinstance(repository, IJobRepository):
        repository = repository()
    return repository
