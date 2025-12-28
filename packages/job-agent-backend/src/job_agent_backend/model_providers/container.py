"""Local dependency injection container for model providers."""

from typing import Any, Callable, Dict

from dependency_injector import containers, providers

from .factory import ModelFactory
from ..contracts.model_factory_interface import IModelFactory
from .mappers import MODEL_PROVIDER_MAP, PROVIDER_MAP
from .providers import OllamaProvider, TransformersProvider
from .registry import ModelRegistry
from .contracts.registry_interface import IModelRegistry


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


def get_model_factory() -> IModelFactory:
    """Get the model factory from the container."""
    return container.model_factory()


def get_model_registry() -> IModelRegistry:
    """Get the model registry from the container."""
    return container.model_registry()


# Type-safe dependency resolution mapping
_DEPENDENCY_MAP: Dict[type, Callable[[], Any]] = {
    IModelFactory: get_model_factory,
    IModelRegistry: get_model_registry,
}


def get(dependency_type: type) -> Any:
    """Get a dependency from the model providers container by its type.

    Note: For type-safe access, prefer using the specific getter functions:
    - get_model_factory() -> IModelFactory
    - get_model_registry() -> IModelRegistry

    Args:
        dependency_type: The type (interface or class) of the dependency to retrieve

    Returns:
        The resolved dependency instance

    Raises:
        KeyError: If the dependency type is not registered in the container

    Examples:
        from job_agent_backend.model_providers.container import get_model_factory

        factory = get_model_factory()
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
