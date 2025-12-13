"""Tests for BaseModelProvider class."""

from typing import Any

from job_agent_backend.model_providers.providers.base import BaseModelProvider


class ConcreteProvider(BaseModelProvider):
    """Concrete implementation for testing abstract BaseModelProvider."""

    def get_model(self) -> Any:
        return "mock_model"


class TestBaseModelProvider:
    """Tests for BaseModelProvider abstract class."""

    def test_stores_model_name(self) -> None:
        provider = ConcreteProvider(model_name="test-model")

        assert provider.model_name == "test-model"

    def test_stores_temperature_with_default(self) -> None:
        provider = ConcreteProvider(model_name="test-model")

        assert provider.temperature == 0.0

    def test_stores_custom_temperature(self) -> None:
        provider = ConcreteProvider(model_name="test-model", temperature=0.7)

        assert provider.temperature == 0.7

    def test_stores_kwargs(self) -> None:
        provider = ConcreteProvider(model_name="test-model", max_tokens=100, top_p=0.9)

        assert provider.kwargs == {"max_tokens": 100, "top_p": 0.9}

    def test_stores_empty_kwargs_by_default(self) -> None:
        provider = ConcreteProvider(model_name="test-model")

        assert provider.kwargs == {}

    def test_repr_returns_formatted_string(self) -> None:
        provider = ConcreteProvider(model_name="test-model", temperature=0.5)

        result = repr(provider)

        assert result == "ConcreteProvider(model=test-model, temp=0.5)"

    def test_repr_uses_class_name(self) -> None:
        class CustomProvider(BaseModelProvider):
            def get_model(self) -> Any:
                return None

        provider = CustomProvider(model_name="my-model", temperature=0.3)

        result = repr(provider)

        assert result == "CustomProvider(model=my-model, temp=0.3)"
