"""Tests for OpenAIProvider class."""

import os
from unittest.mock import MagicMock, patch

import pytest
from pydantic import SecretStr

from job_agent_backend.model_providers.providers.openai import OpenAIProvider


class TestOpenAIProviderInit:
    """Tests for OpenAIProvider initialization."""

    def test_stores_api_key_from_parameter(self) -> None:
        provider = OpenAIProvider(model_name="gpt-4", api_key="test-api-key")

        assert provider.api_key == "test-api-key"

    def test_uses_api_key_from_environment(self) -> None:
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-api-key"}):
            provider = OpenAIProvider(model_name="gpt-4")

        assert provider.api_key == "env-api-key"

    def test_parameter_api_key_overrides_environment(self) -> None:
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-api-key"}):
            provider = OpenAIProvider(model_name="gpt-4", api_key="param-api-key")

        assert provider.api_key == "param-api-key"

    def test_raises_error_when_api_key_missing(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("OPENAI_API_KEY", None)

            with pytest.raises(ValueError, match="OpenAI API key not provided"):
                OpenAIProvider(model_name="gpt-4")

    def test_uses_default_model_name(self) -> None:
        provider = OpenAIProvider(api_key="test-key")

        assert provider.model_name == "gpt-4o-mini"

    def test_stores_custom_model_name(self) -> None:
        provider = OpenAIProvider(model_name="gpt-4-turbo", api_key="test-key")

        assert provider.model_name == "gpt-4-turbo"

    def test_uses_default_temperature(self) -> None:
        provider = OpenAIProvider(api_key="test-key")

        assert provider.temperature == 0.0

    def test_stores_custom_temperature(self) -> None:
        provider = OpenAIProvider(api_key="test-key", temperature=0.7)

        assert provider.temperature == 0.7

    def test_stores_additional_kwargs(self) -> None:
        provider = OpenAIProvider(api_key="test-key", max_tokens=100, top_p=0.9)

        assert provider.kwargs == {"max_tokens": 100, "top_p": 0.9}


class TestOpenAIProviderGetModel:
    """Tests for OpenAIProvider.get_model method."""

    def test_returns_chat_openai_instance(self) -> None:
        mock_chat_openai = MagicMock()

        with patch("langchain_openai.ChatOpenAI", mock_chat_openai):
            provider = OpenAIProvider(model_name="gpt-4", api_key="test-key", temperature=0.5)
            result = provider.get_model()

        mock_chat_openai.assert_called_once_with(
            model="gpt-4", temperature=0.5, api_key=SecretStr("test-key")
        )
        assert result == mock_chat_openai.return_value

    def test_passes_kwargs_to_chat_openai(self) -> None:
        mock_chat_openai = MagicMock()

        with patch("langchain_openai.ChatOpenAI", mock_chat_openai):
            provider = OpenAIProvider(
                model_name="gpt-4", api_key="test-key", max_tokens=100, top_p=0.9
            )
            provider.get_model()

        mock_chat_openai.assert_called_once_with(
            model="gpt-4",
            temperature=0.0,
            api_key=SecretStr("test-key"),
            max_tokens=100,
            top_p=0.9,
        )
