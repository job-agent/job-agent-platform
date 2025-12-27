"""OpenAI provider implementation."""

import os
from typing import Any, Optional

from pydantic import SecretStr

from .base import BaseModelProvider


class OpenAIProvider(BaseModelProvider):
    """OpenAI chat model provider using LangChain's ChatOpenAI."""

    _api_key: SecretStr

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.0,
        api_key: Optional[str] = None,
        **kwargs: Any,
    ):
        """Initialize OpenAI provider.

        Args:
            model_name: OpenAI model name (e.g., 'gpt-4o-mini', 'gpt-4')
            temperature: Temperature for generation
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            **kwargs: Additional ChatOpenAI parameters
        """
        super().__init__(model_name, temperature, **kwargs)
        resolved_key = api_key or os.getenv("OPENAI_API_KEY")

        if not resolved_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment "
                "variable or pass api_key parameter."
            )
        self._api_key = SecretStr(resolved_key)

    @property
    def api_key(self) -> str:
        """Return the API key value for backward compatibility."""
        return self._api_key.get_secret_value()

    def get_model(self) -> Any:
        """Get ChatOpenAI model instance."""
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError(
                "langchain-openai not installed. Install it with: pip install langchain-openai"
            )

        return ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self._api_key,
            **self.kwargs,
        )
