"""Dependency injection container for backend components."""

from dependency_injector import containers, providers

from cvs_repository import CVRepository
from job_agent_backend.core.orchestrator import JobAgentOrchestrator
from job_agent_backend.cv_loader import CVLoader
from job_agent_backend.filter_service.filter import FilterService
from job_agent_backend.messaging import ScrapperClient
from jobs_repository import init_db
from jobs_repository.container import get_job_repository


class ApplicationContainer(containers.DeclarativeContainer):
    """Configure dependency providers for the backend application."""

    config = providers.Configuration()

    scrapper_manager = providers.Singleton(ScrapperClient)

    cv_repository_class = providers.Object(CVRepository)
    cv_loader = providers.Singleton(CVLoader)
    job_repository_factory = providers.Object(get_job_repository)
    filter_service = providers.Singleton(
        FilterService,
        job_repository_factory=job_repository_factory,
    )
    database_initializer = providers.Object(init_db)

    orchestrator = providers.Factory(
        JobAgentOrchestrator,
        cv_repository_class=cv_repository_class,
        cv_loader=cv_loader,
        job_repository_factory=job_repository_factory,
        scrapper_manager=scrapper_manager,
        filter_service=filter_service,
        database_initializer=database_initializer,
    )


container = ApplicationContainer()
