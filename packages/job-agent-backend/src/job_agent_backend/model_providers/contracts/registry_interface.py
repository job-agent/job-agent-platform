"""Abstract interface for model registry."""

from abc import ABC, abstractmethod
from typing import Any, List, Optional

from .provider_interface import IModelProvider


class IModelRegistry(ABC):
    """Interface for model registry that stores pre-configured model providers.

    This abstraction allows for dependency injection and makes testing easier
    by enabling mock implementations.
    """

    @abstractmethod
    def get(self, model_id: str) -> Optional[IModelProvider]:
        """Get a provider by model ID.

        Args:
            model_id: The identifier of the model to retrieve

        Returns:
            The model provider if found, None otherwise
        """
        ...

    @abstractmethod
    def get_model(self, model_id: str) -> Any:
        """Get model instance by ID.

        Args:
            model_id: The identifier of the model to retrieve

        Returns:
            The model instance

        Raises:
            ValueError: If the model ID is not found
        """
        ...

    @abstractmethod
    def list_models(self) -> List[str]:
        """List all registered model IDs.

        Returns:
            List of registered model identifiers
        """
        ...
