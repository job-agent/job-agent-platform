"""Factory class for creating AI model instances."""

from typing import Any, Dict, Optional, Type

from ..contracts.model_factory_interface import IModelFactory
from .mappers import MODEL_PROVIDER_MAP
from .contracts.provider_interface import IModelProvider
from .contracts.registry_interface import IModelRegistry


class ModelFactory(IModelFactory):
    """Factory class for creating and caching AI model instances."""

    def __init__(
        self,
        registry: IModelRegistry,
        provider_map: Dict[str, Type[IModelProvider]],
        model_provider_map: Optional[Dict[str, str]] = None,
    ) -> None:
        """Initialize the model factory with injected dependencies.

        Args:
            registry: The model registry for pre-configured models
            provider_map: Mapping of provider names to provider classes
            model_provider_map: Optional mapping of model names to provider names
                              for auto-detection. Defaults to MODEL_PROVIDER_MAP.
        """
        self._registry = registry
        self._provider_map = provider_map
        self._model_provider_map = (
            model_provider_map if model_provider_map is not None else MODEL_PROVIDER_MAP
        )
        self._model_cache: Dict[str, Any] = {}

    def _generate_cache_key(
        self, provider: str, model_name: str, temperature: float, kwargs: dict
    ) -> str:
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
        """Get an AI model instance.

        Args:
            model_id: ID of a pre-configured model (e.g., "skill-extraction")
            provider: Provider type ("openai", "ollama", "transformers")
            model_name: Model name (e.g., "gpt-4o-mini", "phi3:mini")
            temperature: Generation temperature
            **kwargs: Additional provider-specific parameters

        Returns:
            An AI model instance
        """
        # Use pre-configured provider from registry
        if model_id:
            provider_instance = self._registry.get(model_id)
            if not provider_instance:
                raise ValueError(
                    f"Model '{model_id}' not found. " f"Available: {self._registry.list_models()}"
                )
            # Cache key for registered models
            cache_key = f"registered:{model_id}"
            if cache_key not in self._model_cache:
                self._model_cache[cache_key] = provider_instance.get_model()
            return self._model_cache[cache_key]

        # Create provider on-the-fly
        if not model_name:
            raise ValueError("Either 'model_id' or 'model_name' must be provided")

        # Auto-detect provider if not specified
        if not provider:
            provider = self._model_provider_map.get(model_name)
            if not provider:
                raise ValueError(
                    f"Cannot auto-detect provider for '{model_name}'. "
                    f"Specify 'provider' explicitly."
                )

        provider_class = self._provider_map.get(provider.lower())
        if not provider_class:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported: {list(self._provider_map.keys())}"
            )

        final_temperature = temperature if temperature is not None else 0.0

        cache_key = self._generate_cache_key(provider, model_name, final_temperature, kwargs)
        if cache_key in self._model_cache:
            return self._model_cache[cache_key]

        provider_instance = provider_class(
            model_name=model_name, temperature=final_temperature, **kwargs
        )
        model = provider_instance.get_model()
        self._model_cache[cache_key] = model
        return model

    def clear_cache(self) -> None:
        self._model_cache.clear()

    def get_cache_size(self) -> int:
        return len(self._model_cache)
