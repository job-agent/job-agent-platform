"""Dependency injection container for backend components."""

from typing import Any, Callable, Dict

from dependency_injector import containers, providers

from cvs_repository import CVRepository
from essay_repository import get_essay_repository
from job_agent_backend.core.orchestrator import JobAgentOrchestrator
from job_agent_backend.contracts import IEssaySearchService
from job_agent_backend.cv_loader import CVLoader, ICVLoader
from job_agent_backend.filter_service import FilterService, IFilterService
from job_agent_backend.messaging import ScrapperClient, IScrapperClient
from job_agent_backend.model_providers import IModelFactory
from job_agent_backend.model_providers.container import get_model_factory
from job_agent_backend.services import EssaySearchService
from job_agent_backend.services.keyword_generation import KeywordGenerator
from job_agent_platform_contracts import IJobAgentOrchestrator
from jobs_repository import init_db
from jobs_repository.container import get_job_repository


class ApplicationContainer(containers.DeclarativeContainer):
    """Configure dependency providers for the backend application."""

    config = providers.Configuration()

    cv_repository = providers.Object(CVRepository)
    cv_loader = providers.Singleton(CVLoader)
    job_repository_factory = providers.Object(get_job_repository)

    # Model factory from model_providers container
    model_factory = providers.Factory(get_model_factory)

    scrapper_manager = providers.Singleton(
        ScrapperClient,
        job_repository_factory=job_repository_factory,
    )
    filter_service = providers.Singleton(
        FilterService,
        job_repository_factory=job_repository_factory,
    )
    database_initializer = providers.Object(init_db)

    # Essay repository and search service
    essay_repository_factory = providers.Factory(get_essay_repository)
    keyword_generator = providers.Factory(
        KeywordGenerator,
        model_factory=model_factory,
        repository=essay_repository_factory,
    )
    essay_search_service = providers.Factory(
        EssaySearchService,
        repository=essay_repository_factory,
        model_factory=model_factory,
        keyword_generator=keyword_generator,
    )

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


# Type-safe getter functions for each dependency
def get_model_factory_instance() -> IModelFactory:
    """Get the model factory from the container."""
    return container.model_factory()


def get_cv_loader() -> ICVLoader:
    """Get the CV loader from the container."""
    return container.cv_loader()


def get_scrapper_client() -> IScrapperClient:
    """Get the scrapper client from the container."""
    return container.scrapper_manager()


def get_filter_service() -> IFilterService:
    """Get the filter service from the container."""
    return container.filter_service()


def get_orchestrator() -> IJobAgentOrchestrator:
    """Get the orchestrator from the container."""
    return container.orchestrator()


def get_essay_search_service() -> IEssaySearchService:
    """Get the essay search service from the container."""
    return container.essay_search_service()


# Type-safe dependency resolution mapping
_DEPENDENCY_MAP: Dict[type, Callable[[], Any]] = {
    IModelFactory: get_model_factory_instance,
    ICVLoader: get_cv_loader,
    IScrapperClient: get_scrapper_client,
    IFilterService: get_filter_service,
    IJobAgentOrchestrator: get_orchestrator,
    IEssaySearchService: get_essay_search_service,
}


def get(dependency_type: type) -> Any:
    """Get a dependency from the container by its type.

    Note: For type-safe access, prefer using the specific getter functions:
    - get_model_factory_instance() -> IModelFactory
    - get_cv_loader() -> ICVLoader
    - get_scrapper_client() -> IScrapperClient
    - get_filter_service() -> IFilterService
    - get_orchestrator() -> IJobAgentOrchestrator
    - get_essay_search_service() -> IEssaySearchService

    Args:
        dependency_type: The type (interface or class) of the dependency to retrieve

    Returns:
        The resolved dependency instance

    Raises:
        KeyError: If the dependency type is not registered in the container

    Examples:
        from job_agent_backend.container import get_model_factory_instance

        factory = get_model_factory_instance()
        model = factory.get_model(model_id="skill-extraction")
    """
    resolver = _DEPENDENCY_MAP.get(dependency_type)
    if resolver is None:
        dep_name = getattr(dependency_type, "__name__", str(dependency_type))
        available = ", ".join(t.__name__ for t in _DEPENDENCY_MAP.keys())
        raise KeyError(
            f"Dependency '{dep_name}' not found in container. Available types: {available}"
        )
    return resolver()
