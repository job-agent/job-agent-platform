"""Factory class for creating AI model instances."""

from typing import Any, Dict, Optional

from .config import get_model_config
from .interfaces import IModelFactory
from .model_provider_map import MODEL_PROVIDER_MAP
from .providers import OpenAIProvider, TransformersProvider, OllamaProvider


class ModelFactory(IModelFactory):
    """Factory class for creating and caching AI model instances.

    This class provides flexible model creation with multiple usage patterns:

    1. Use a pre-configured model by ID:
        factory = ModelFactory()
        model = factory.get_model(model_id="default")

    2. Override a configured model's parameters:
        model = factory.get_model(model_id="default", temperature=0.5)

    3. Use a known model (auto-detects provider):
        model = factory.get_model(model_name="phi3:mini")
        model = factory.get_model(model_name="gpt-4o-mini")

    4. Explicitly specify provider and model:
        model = factory.get_model(provider="openai", model_name="gpt-4")
    """

    # Provider class mapping
    PROVIDER_MAP = {
        "openai": OpenAIProvider,
        "transformers": TransformersProvider,
        "ollama": OllamaProvider,
    }

    def __init__(self) -> None:
        """Initialize the ModelFactory with an empty cache."""
        self._model_cache: Dict[str, Any] = {}

    def _generate_cache_key(
        self, provider: str, model_name: str, temperature: float, kwargs: dict
    ) -> str:
        """Generate a cache key from model configuration.

        Args:
            provider: Provider type (e.g., "openai", "ollama")
            model_name: Model name
            temperature: Generation temperature
            kwargs: Additional parameters

        Returns:
            String cache key
        """
        # Sort kwargs for consistent key generation
        kwargs_str = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return f"{provider}:{model_name}:temp={temperature}:{kwargs_str}"

    def get_model(
        self,
        model_id: Optional[str] = None,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> Any:
        """Get an AI model instance based on configuration.

        Args:
            model_id: ID of a pre-configured model (e.g., "default", "skill-extraction")
            provider: Provider type ("openai", "ollama", "transformers") - auto-detected if not specified
            model_name: Model name - provider will be auto-detected from mapping if available
            temperature: Generation temperature - overrides config
            **kwargs: Additional provider-specific parameters

        Returns:
            An AI model instance (e.g., LangChain chat model, embedding model, etc.)

        Raises:
            ValueError: If neither model_id nor (provider + model_name) are provided
            ValueError: If model_id is not found in configuration
            ValueError: If provider type is not supported

        Examples:
            # Use pre-configured model
            factory = ModelFactory()
            model = factory.get_model(model_id="default")

            # Override temperature for a configured model
            model = factory.get_model(model_id="skill-extraction", temperature=0.7)

            # Create custom model
            model = factory.get_model(provider="openai", model_name="gpt-4")

            # Use with structured output (for chat models)
            structured_model = factory.get_model(model_id="default").with_structured_output(MySchema)
        """
        config = None

        # Load configuration if model_id is provided
        if model_id:
            config = get_model_config(model_id)
            if not config:
                raise ValueError(
                    f"Model '{model_id}' not found in configuration. "
                    f"Available models: {list(get_model_config.__globals__['_registry'].list_models().keys())}"
                )

        # If no config and no provider/model_name, error
        if not config and not (provider and model_name):
            raise ValueError(
                "Either 'model_id' or both 'provider' and 'model_name' must be provided"
            )

        # Determine final parameters (command-line args override config)
        final_model_name = model_name or (config.model_name if config else None)
        final_provider = provider or (config.provider if config else None)

        # Auto-detect provider from model name if not specified
        if not final_provider and final_model_name:
            final_provider = MODEL_PROVIDER_MAP.get(final_model_name)
            if not final_provider:
                raise ValueError(
                    f"Cannot auto-detect provider for model '{final_model_name}'. "
                    f"Either specify 'provider' explicitly or add the model to MODEL_PROVIDER_MAP. "
                    f"Known models: {list(MODEL_PROVIDER_MAP.keys())}"
                )

        final_temperature = (
            temperature if temperature is not None else (config.temperature if config else 0.0)
        )

        # Merge kwargs from config and function call
        final_kwargs = {}
        if config:
            final_kwargs.update(config.kwargs)
        final_kwargs.update(kwargs)

        # Get provider class
        provider_class = self.PROVIDER_MAP.get(final_provider.lower())
        if not provider_class:
            raise ValueError(
                f"Unsupported provider: {final_provider}. "
                f"Supported providers: {list(self.PROVIDER_MAP.keys())}"
            )

        # Generate cache key
        cache_key = self._generate_cache_key(
            final_provider, final_model_name, final_temperature, final_kwargs
        )

        # Return cached model if available
        if cache_key in self._model_cache:
            print(f"  [Cache Hit] Returning cached model for: {final_provider}/{final_model_name}")
            return self._model_cache[cache_key]

        # Instantiate provider and get model
        print(f"  [Cache Miss] Creating new model instance: {final_provider}/{final_model_name}")
        provider_instance = provider_class(
            model_name=final_model_name, temperature=final_temperature, **final_kwargs
        )

        model = provider_instance.get_model()

        # Cache the model instance
        self._model_cache[cache_key] = model

        return model

    def clear_cache(self) -> None:
        """Clear the model cache, forcing new instances to be created."""
        self._model_cache.clear()

    def get_cache_size(self) -> int:
        """Get the number of cached model instances.

        Returns:
            Number of models in the cache
        """
        return len(self._model_cache)


def get_model_factory() -> "ModelFactory":
    """Get the singleton ModelFactory instance from the DI container.

    This function retrieves the ModelFactory from the application's dependency
    injection container, ensuring a single shared instance with consistent cache.

    Returns:
        The singleton ModelFactory instance

    Examples:
        # Get the factory and use it
        factory = get_model_factory()
        model = factory.get_model(model_id="default")

        # Check cache size
        print(f"Cached models: {factory.get_cache_size()}")
    """
    from job_agent_backend.container import get
    from job_agent_backend.model_providers.interfaces import IModelFactory

    # Get by interface type - returns the concrete ModelFactory singleton
    return get(IModelFactory)


def get_model(
    model_id: Optional[str] = None,
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    **kwargs: Any,
) -> Any:
    """Get an AI model instance based on configuration.

    This function provides backward compatibility with the previous function-based API.
    It uses the singleton ModelFactory instance from the DI container.

    For new code, consider using the container directly:
        from job_agent_backend.container import get
        from job_agent_backend.model_providers.interfaces import IModelFactory

        factory = get(IModelFactory)
        model = factory.get_model(model_id="default")

    Or use the helper function:
        from job_agent_backend.model_providers.factory import get_model_factory
        factory = get_model_factory()
        model = factory.get_model(model_id="default")

    Args:
        model_id: ID of a pre-configured model (e.g., "default", "skill-extraction")
        provider: Provider type ("openai", "ollama", "transformers") - auto-detected if not specified
        model_name: Model name - provider will be auto-detected from mapping if available
        temperature: Generation temperature - overrides config
        **kwargs: Additional provider-specific parameters

    Returns:
        An AI model instance (e.g., LangChain chat model, embedding model, etc.)

    Raises:
        ValueError: If neither model_id nor (provider + model_name) are provided
        ValueError: If model_id is not found in configuration
        ValueError: If provider type is not supported

    Examples:
        # Use pre-configured model
        model = get_model(model_id="default")

        # Override temperature for a configured model
        model = get_model(model_id="skill-extraction", temperature=0.7)

        # Create custom model
        model = get_model(provider="openai", model_name="gpt-4")

        # Use with structured output (for chat models)
        structured_model = get_model(model_id="default").with_structured_output(MySchema)
    """
    factory = get_model_factory()
    return factory.get_model(
        model_id=model_id,
        provider=provider,
        model_name=model_name,
        temperature=temperature,
        **kwargs,
    )
