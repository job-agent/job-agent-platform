"""Tests for OllamaProvider class."""

import os
from unittest.mock import MagicMock, patch


from job_agent_backend.model_providers.providers.ollama import OllamaProvider


class TestOllamaProviderInit:
    """Tests for OllamaProvider initialization."""

    def test_uses_default_base_url(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("OLLAMA_BASE_URL", None)
            provider = OllamaProvider(model_name="phi3:mini")

        assert provider.base_url == "http://localhost:11434"

    def test_uses_base_url_from_environment(self) -> None:
        with patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://custom:8080"}):
            provider = OllamaProvider(model_name="phi3:mini")

        assert provider.base_url == "http://custom:8080"

    def test_parameter_base_url_overrides_environment(self) -> None:
        with patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://env:8080"}):
            provider = OllamaProvider(model_name="phi3:mini", base_url="http://param:9090")

        assert provider.base_url == "http://param:9090"

    def test_stores_model_name(self) -> None:
        provider = OllamaProvider(model_name="phi3:mini")

        assert provider.model_name == "phi3:mini"

    def test_stores_custom_model_name(self) -> None:
        provider = OllamaProvider(model_name="llama3")

        assert provider.model_name == "llama3"

    def test_uses_default_temperature(self) -> None:
        provider = OllamaProvider(model_name="phi3:mini")

        assert provider.temperature == 0.0

    def test_stores_custom_temperature(self) -> None:
        provider = OllamaProvider(model_name="phi3:mini", temperature=0.7)

        assert provider.temperature == 0.7

    def test_stores_additional_kwargs(self) -> None:
        provider = OllamaProvider(model_name="phi3:mini", num_ctx=4096, repeat_penalty=1.1)

        assert provider.kwargs == {"num_ctx": 4096, "repeat_penalty": 1.1}


class TestOllamaProviderGetModel:
    """Tests for OllamaProvider.get_model method."""

    def test_returns_chat_ollama_instance(self) -> None:
        mock_chat_ollama = MagicMock()

        with patch("langchain_ollama.ChatOllama", mock_chat_ollama):
            provider = OllamaProvider(
                model_name="phi3:mini", temperature=0.5, base_url="http://test:11434"
            )
            result = provider.get_model()

        mock_chat_ollama.assert_called_once_with(
            model="phi3:mini",
            temperature=0.5,
            base_url="http://test:11434",
        )
        assert result == mock_chat_ollama.return_value

    def test_passes_kwargs_to_chat_ollama(self) -> None:
        mock_chat_ollama = MagicMock()

        with patch("langchain_ollama.ChatOllama", mock_chat_ollama):
            provider = OllamaProvider(model_name="phi3:mini", num_ctx=4096, repeat_penalty=1.1)
            provider.get_model()

        mock_chat_ollama.assert_called_once_with(
            model="phi3:mini",
            temperature=0.0,
            base_url=provider.base_url,
            num_ctx=4096,
            repeat_penalty=1.1,
        )
