"""Model configuration registry."""

from typing import Any, Dict, List, Optional

from .providers import IModelProvider, OllamaProvider, TransformersProvider


class ModelRegistry:
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


_registry = ModelRegistry([
    ("skill-extraction", OllamaProvider(model_name="phi3:mini", temperature=0.0)),
    ("pii-removal", OllamaProvider(model_name="phi3:mini", temperature=0.0)),
    ("embedding", TransformersProvider(
        model_name="sentence-transformers/distiluse-base-multilingual-cased-v2",
        task="embedding",
    )),
])
