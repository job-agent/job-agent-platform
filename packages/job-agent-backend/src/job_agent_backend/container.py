"""Dependency injection container for backend components."""

from typing import Type, TypeVar, overload

from dependency_injector import containers, providers

from cvs_repository import CVRepository
from job_agent_backend.core.orchestrator import JobAgentOrchestrator
from job_agent_backend.cv_loader import CVLoader, ICVLoader
from job_agent_backend.filter_service import FilterService, IFilterService
from job_agent_backend.messaging import ScrapperClient, IScrapperClient
from job_agent_backend.model_providers import IModelFactory, ModelFactory
from job_agent_backend.model_providers.container import (
    get as get_model_provider,
)
from job_agent_platform_contracts import IJobAgentOrchestrator
from jobs_repository import init_db
from jobs_repository.container import get_job_repository

T = TypeVar("T")


class ApplicationContainer(containers.DeclarativeContainer):
    """Configure dependency providers for the backend application."""

    config = providers.Configuration()

    cv_repository = providers.Object(CVRepository)
    cv_loader = providers.Singleton(CVLoader)
    job_repository_factory = providers.Object(get_job_repository)

    # Model factory from model_providers container
    model_factory = providers.Object(get_model_provider(IModelFactory))

    scrapper_manager = providers.Singleton(
        ScrapperClient,
        job_repository_factory=job_repository_factory,
    )
    filter_service = providers.Singleton(
        FilterService,
        job_repository_factory=job_repository_factory,
    )
    database_initializer = providers.Object(init_db)

    orchestrator = providers.Factory(
        JobAgentOrchestrator,
        cv_repository_class=cv_repository,
        cv_loader=cv_loader,
        job_repository_factory=job_repository_factory,
        scrapper_manager=scrapper_manager,
        filter_service=filter_service,
        database_initializer=database_initializer,
    )


container = ApplicationContainer()


# Type-safe dependency resolution mapping
# Maps interface types to their concrete implementations in the container
_DEPENDENCY_MAP = {
    # Model factory retrieved from model_providers container
    IModelFactory: lambda: container.model_factory(),
    ICVLoader: lambda: container.cv_loader(),
    IScrapperClient: lambda: container.scrapper_manager(),
    IFilterService: lambda: container.filter_service(),
    IJobAgentOrchestrator: lambda: container.orchestrator(),
}


# Type overloads for IDE autocomplete and type checking
@overload
def get(dependency_type: Type[IModelFactory]) -> IModelFactory: ...


@overload
def get(dependency_type: Type[ICVLoader]) -> ICVLoader: ...


@overload
def get(dependency_type: Type[IScrapperClient]) -> IScrapperClient: ...


@overload
def get(dependency_type: Type[IFilterService]) -> IFilterService: ...


@overload
def get(dependency_type: Type[IJobAgentOrchestrator]) -> IJobAgentOrchestrator: ...


# Concrete types (for backward compatibility)
@overload
def get(dependency_type: Type[ModelFactory]) -> ModelFactory: ...


@overload
def get(dependency_type: Type[CVLoader]) -> CVLoader: ...


@overload
def get(dependency_type: Type[ScrapperClient]) -> ScrapperClient: ...


@overload
def get(dependency_type: Type[FilterService]) -> FilterService: ...


@overload
def get(dependency_type: Type[JobAgentOrchestrator]) -> JobAgentOrchestrator: ...


def get(dependency_type: Type[T]) -> T:
    """Get a dependency from the container by its type.

    This provides a type-safe way to resolve dependencies using types
    (either interfaces or concrete classes) instead of provider names.
    Works with both abstract interfaces (protocols) and concrete classes.

    Args:
        dependency_type: The type (interface or class) of the dependency to retrieve

    Returns:
        The resolved dependency instance

    Raises:
        KeyError: If the dependency type is not registered in the container

    Examples:
        # Using interface type (recommended - loose coupling)
        from job_agent_backend.container import get
        from job_agent_backend.model_providers import IModelFactory

        factory = get(IModelFactory)
        model = factory.get_model(model_id="skill-extraction")

        # Other services
        from job_agent_backend.messaging import IScrapperClient
        scrapper = get(IScrapperClient)
    """
    resolver = _DEPENDENCY_MAP.get(dependency_type)
    if resolver is None:
        raise KeyError(
            f"Dependency '{dependency_type.__name__}' not found in container. "
            f"Available types: {', '.join(t.__name__ for t in _DEPENDENCY_MAP.keys())}"
        )
    return resolver()
