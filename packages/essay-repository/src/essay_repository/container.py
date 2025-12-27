"""Dependency injection container for essay repository services."""

from typing import Any, Callable, Type, TypeVar

from dependency_injector import containers, providers
from job_agent_platform_contracts.essay_repository import (
    IEssayRepository,
)

from db_core import get_session_factory
from essay_repository.repository.essay_repository import EssayRepository


T = TypeVar("T")


class EssayRepositoryContainer(containers.DeclarativeContainer):
    """Configure dependency providers for the essay repository package."""

    config = providers.Configuration()

    session_factory = providers.Singleton(get_session_factory)

    essay_repository = providers.Factory(
        EssayRepository,
        session_factory=session_factory,
    )


container = EssayRepositoryContainer()


_DEPENDENCY_MAP: dict[Type[Any], Callable[[], Any]] = {
    IEssayRepository: lambda: container.essay_repository(),
}


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


def get_essay_repository() -> IEssayRepository:
    """Get an essay repository instance.

    This is a convenience function for use as a factory in DI containers.
    Equivalent to calling get(IEssayRepository).

    Returns:
        A configured EssayRepository instance
    """
    return container.essay_repository()
