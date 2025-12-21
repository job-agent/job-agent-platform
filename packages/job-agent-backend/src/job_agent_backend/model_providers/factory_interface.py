"""Abstract interface for model factory."""

from abc import ABC, abstractmethod
from typing import Any, Optional

# Type alias for model instances returned by the factory.
# We use Any because the factory can return various model types
# (LangChain ChatModel, Embeddings, HuggingFace pipelines, etc.)
# and there is no common base class across these libraries.
ModelInstance = Any


class IModelFactory(ABC):
    """Protocol defining the interface for model factories.

    This abstraction allows for dependency injection and makes testing easier
    by enabling mock implementations.
    """

    @abstractmethod
    def get_model(
        self,
        model_id: Optional[str] = None,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> ModelInstance:
        """Get an AI model instance based on configuration.

        Args:
            model_id: ID of a pre-configured model (e.g., "default", "skill-extraction")
            provider: Provider type ("openai", "ollama", "transformers")
            model_name: Model name
            temperature: Generation temperature
            **kwargs: Additional provider-specific parameters

        Returns:
            An AI model instance
        """
        ...

    @abstractmethod
    def clear_cache(self) -> None:
        """Clear the model cache, forcing new instances to be created."""
        ...

    @abstractmethod
    def get_cache_size(self) -> int:
        """Get the number of cached model instances.

        Returns:
            Number of models in the cache
        """
        ...
