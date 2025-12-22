"""Dependency injection container for essay repository services."""

from dependency_injector import containers, providers
from job_agent_platform_contracts.essay_repository import IEssayRepository

from db_core import get_session_factory
from essay_repository.repository.essay_repository import EssayRepository


class EssayRepositoryContainer(containers.DeclarativeContainer):
    """Configure dependency providers for the essay repository package."""

    config = providers.Configuration()

    session_factory = providers.Singleton(get_session_factory)

    essay_repository = providers.Factory(
        EssayRepository,
        session_factory=session_factory,
    )


container = EssayRepositoryContainer()


def get_essay_repository() -> IEssayRepository:
    """Provide an EssayRepository instance with managed session lifecycle."""
    repository = container.essay_repository()
    if callable(repository) and not isinstance(repository, IEssayRepository):
        repository = repository()
    return repository
