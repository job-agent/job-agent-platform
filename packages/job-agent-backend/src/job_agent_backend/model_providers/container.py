"""Local dependency injection container for model providers."""

from typing import Type, TypeVar, overload

from dependency_injector import containers, providers

from .factory import ModelFactory
from ..contracts.model_factory_interface import IModelFactory
from .mappers import MODEL_PROVIDER_MAP, PROVIDER_MAP
from .providers import OllamaProvider, TransformersProvider
from .registry import ModelRegistry
from .contracts.registry_interface import IModelRegistry

T = TypeVar("T")


class ModelProvidersContainer(containers.DeclarativeContainer):
    """Container for model providers dependencies.

    This container manages all model provider components including
    the registry with pre-configured models and the model factory.
    """

    # Map providers (Object providers - return the dictionaries as-is)
    provider_map = providers.Object(PROVIDER_MAP)
    model_provider_map = providers.Object(MODEL_PROVIDER_MAP)

    # Model registry with pre-configured providers
    model_registry = providers.Singleton(
        ModelRegistry,
        providers=[
            (
                "skill-extraction",
                OllamaProvider(model_name="phi3:mini", temperature=0.0),
            ),
            (
                "pii-removal",
                OllamaProvider(model_name="phi3:mini", temperature=0.0),
            ),
            (
                "embedding",
                TransformersProvider(
                    model_name="sentence-transformers/distiluse-base-multilingual-cased-v2",
                    task="embedding",
                ),
            ),
        ],
    )

    # Model factory singleton - maintains model cache
    model_factory = providers.Singleton(
        ModelFactory,
        registry=model_registry,
        provider_map=provider_map,
        model_provider_map=model_provider_map,
    )


container = ModelProvidersContainer()


# Type-safe dependency resolution mapping
_DEPENDENCY_MAP = {
    IModelFactory: lambda: container.model_factory(),
    IModelRegistry: lambda: container.model_registry(),
}


@overload
def get(dependency_type: Type[IModelFactory]) -> IModelFactory: ...


@overload
def get(dependency_type: Type[IModelRegistry]) -> IModelRegistry: ...


@overload
def get(dependency_type: Type[ModelFactory]) -> ModelFactory: ...


@overload
def get(dependency_type: Type[ModelRegistry]) -> ModelRegistry: ...


def get(dependency_type: Type[T]) -> T:
    """Get a dependency from the model providers container by its type.

    Args:
        dependency_type: The type (interface or class) of the dependency to retrieve

    Returns:
        The resolved dependency instance

    Raises:
        KeyError: If the dependency type is not registered in the container

    Examples:
        from job_agent_backend.model_providers.container import get
        from job_agent_backend.model_providers import IModelFactory

        factory = get(IModelFactory)
        model = factory.get_model(model_id="skill-extraction")
    """
    resolver = _DEPENDENCY_MAP.get(dependency_type)
    if resolver is None:
        raise KeyError(
            f"Dependency '{dependency_type.__name__}' not found in container. "
            f"Available types: {', '.join(t.__name__ for t in _DEPENDENCY_MAP.keys())}"
        )
    return resolver()
