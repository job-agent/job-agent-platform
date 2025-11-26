"""Base provider interface for AI model implementations."""

from abc import ABC, abstractmethod
from typing import Any


class BaseModelProvider(ABC):
    """Abstract base class for all AI model providers.

    All provider implementations (OpenAI, Ollama, Transformers, etc.) must inherit
    from this class and implement the get_model method.

    This supports various model types: chat models, embeddings, classifiers, etc.
    """

    def __init__(self, model_name: str, temperature: float = 0.0, **kwargs: Any):
        """Initialize the provider.

        Args:
            model_name: Name/identifier of the model to use
            temperature: Temperature for generation (0.0 = deterministic)
            **kwargs: Additional provider-specific parameters
        """
        self.model_name = model_name
        self.temperature = temperature
        self.kwargs = kwargs

    @abstractmethod
    def get_model(self) -> Any:
        """Get the model instance.

        Returns:
            A model instance (e.g., LangChain chat model, embedding model, etc.)
            The specific interface depends on the model type.
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model_name}, temp={self.temperature})"
