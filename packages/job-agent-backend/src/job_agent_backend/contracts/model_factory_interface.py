"""Abstract interface for model factory."""

from typing import TYPE_CHECKING, Any, Literal, Optional, Protocol, overload

if TYPE_CHECKING:
    from langchain_core.embeddings import Embeddings
    from langchain_core.language_models import BaseChatModel

    from job_agent_backend.model_providers.contracts.provider_interface import ModelInstance
else:
    ModelInstance = Any
    Embeddings = Any
    BaseChatModel = Any


class IModelFactory(Protocol):
    """Protocol defining the interface for model factories.

    This abstraction allows for dependency injection and makes testing easier
    by enabling mock implementations.
    """

    @overload
    def get_model(
        self,
        model_id: Literal["embedding"],
        provider: None = None,
        model_name: None = None,
        temperature: None = None,
    ) -> "Embeddings": ...

    @overload
    def get_model(
        self,
        model_id: Literal["pii-removal", "skill-extraction", "keyword-extraction"],
        provider: None = None,
        model_name: None = None,
        temperature: None = None,
    ) -> "BaseChatModel": ...

    @overload
    def get_model(
        self,
        model_id: Optional[str] = None,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> ModelInstance: ...

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
            An AI model instance (BaseChatModel, Embeddings, or Pipeline)
        """
        ...

    def clear_cache(self) -> None:
        """Clear the model cache, forcing new instances to be created."""
        ...

    def get_cache_size(self) -> int:
        """Get the number of cached model instances.

        Returns:
            Number of models in the cache
        """
        ...
