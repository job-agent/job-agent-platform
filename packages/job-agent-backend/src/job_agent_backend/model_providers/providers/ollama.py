"""Ollama provider implementation."""

import os
from typing import Any, Optional

from .base import BaseModelProvider


class OllamaProvider(BaseModelProvider):
    """Ollama model provider using LangChain's ChatOllama."""

    def __init__(
        self,
        model_name: str = "phi3:mini",
        temperature: float = 0.0,
        base_url: Optional[str] = None,
        **kwargs: Any,
    ):
        """Initialize Ollama provider.

        Args:
            model_name: Ollama model name (e.g., 'phi3:mini', 'llama3')
            temperature: Temperature for generation
            base_url: Ollama base URL (defaults to OLLAMA_BASE_URL env var or http://localhost:11434)
            **kwargs: Additional ChatOllama parameters
        """
        super().__init__(model_name, temperature, **kwargs)
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def get_model(self) -> Any:
        """Get ChatOllama model instance."""
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            raise ImportError(
                "langchain-ollama not installed. " "Install it with: pip install langchain-ollama"
            )

        return ChatOllama(
            model=self.model_name,
            temperature=self.temperature,
            base_url=self.base_url,
            **self.kwargs,
        )
