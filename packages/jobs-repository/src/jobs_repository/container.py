"""Dependency injection container for jobs repository services."""

from typing import Type, TypeVar, overload

from dependency_injector import containers, providers
from job_agent_platform_contracts import IJobRepository

from db_core import get_session_factory
from jobs_repository.repository.job_repository import JobRepository
from jobs_repository.services import ReferenceDataService
from jobs_repository.mapper import JobMapper


T = TypeVar("T")


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


_DEPENDENCY_MAP = {
    IJobRepository: lambda: container.job_repository(),
}


@overload
def get(dependency_type: Type[IJobRepository]) -> IJobRepository: ...


def get(dependency_type: Type[T]) -> T:
    """Get a dependency from the container by its type.

    Args:
        dependency_type: The interface type to retrieve

    Returns:
        The resolved dependency instance

    Raises:
        KeyError: If the dependency type is not registered
    """
    resolver = _DEPENDENCY_MAP.get(dependency_type)
    if resolver is None:
        raise KeyError(
            f"Dependency '{dependency_type.__name__}' not found in container. "
            f"Available types: {', '.join(t.__name__ for t in _DEPENDENCY_MAP.keys())}"
        )
    return resolver()
