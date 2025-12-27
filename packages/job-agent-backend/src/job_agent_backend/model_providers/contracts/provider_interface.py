"""Abstract interface for model providers."""

from typing import Any, Protocol

# Type alias for model instances returned by providers.
# We use Any because providers can return various model types
# (LangChain ChatModel, Embeddings, HuggingFace pipelines, etc.)
# and there is no common base class across these libraries.
ModelInstance = Any


class IModelProvider(Protocol):
    """Protocol for all AI model providers.

    This interface defines the contract that all model providers must implement.
    Concrete implementations (OpenAI, Ollama, Transformers, etc.) inherit from
    BaseModelProvider which implements this interface.
    """

    def get_model(self) -> ModelInstance:
        """Get the model instance.

        Returns:
            A model instance (e.g., LangChain chat model, embedding model, etc.)
            The specific interface depends on the model type.
        """
        ...
