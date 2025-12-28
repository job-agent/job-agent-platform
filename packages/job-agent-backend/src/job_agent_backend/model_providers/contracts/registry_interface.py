"""Abstract interface for model registry."""

from typing import List, Optional, Protocol

from .provider_interface import IModelProvider, ModelInstance


class IModelRegistry(Protocol):
    """Protocol for model registry that stores pre-configured model providers.

    This abstraction allows for dependency injection and makes testing easier
    by enabling mock implementations.
    """

    def get(self, model_id: str) -> Optional[IModelProvider]:
        """Get a provider by model ID.

        Args:
            model_id: The identifier of the model to retrieve

        Returns:
            The model provider if found, None otherwise
        """
        ...

    def get_model(self, model_id: str) -> ModelInstance:
        """Get model instance by ID.

        Args:
            model_id: The identifier of the model to retrieve

        Returns:
            The model instance (BaseChatModel, Embeddings, or Pipeline)

        Raises:
            ValueError: If the model ID is not found
        """
        ...

    def list_models(self) -> List[str]:
        """List all registered model IDs.

        Returns:
            List of registered model identifiers
        """
        ...
