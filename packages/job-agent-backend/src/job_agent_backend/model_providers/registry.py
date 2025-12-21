"""Model configuration registry."""

from typing import Any, Dict, List, Optional

from .providers import IModelProvider
from .registry_interface import IModelRegistry


class ModelRegistry(IModelRegistry):
    """Registry for pre-configured model providers."""

    def __init__(self, providers: List[tuple[str, IModelProvider]]) -> None:
        """Initialize registry with list of (model_id, provider) tuples."""
        self._providers: Dict[str, IModelProvider] = {
            model_id: provider for model_id, provider in providers
        }

    def get(self, model_id: str) -> Optional[IModelProvider]:
        """Get a provider by model ID."""
        return self._providers.get(model_id)

    def get_model(self, model_id: str) -> Any:
        """Get model instance by ID."""
        provider = self._providers.get(model_id)
        if not provider:
            raise ValueError(f"Model '{model_id}' not found")
        return provider.get_model()

    def list_models(self) -> List[str]:
        """List all registered model IDs."""
        return list(self._providers.keys())
