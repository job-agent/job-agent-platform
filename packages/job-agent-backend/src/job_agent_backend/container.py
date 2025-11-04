"""Dependency injection container for backend components."""

from dependency_injector import containers, providers

from cvs_repository import CVRepository
from job_agent_backend.core.orchestrator import JobAgentOrchestrator
from jobs_repository.repository import JobRepository
from scrapper_service import ScrapperManager


class ApplicationContainer(containers.DeclarativeContainer):
    """Configure dependency providers for the backend application."""

    config = providers.Configuration()

    scrapper_manager = providers.Singleton(ScrapperManager)

    cv_repository_class = providers.Object(CVRepository)
    job_repository_class = providers.Object(JobRepository)

    orchestrator = providers.Factory(
        JobAgentOrchestrator,
        cv_repository_class=cv_repository_class,
        job_repository_class=job_repository_class,
        scrapper_manager=scrapper_manager,
    )


container = ApplicationContainer()
