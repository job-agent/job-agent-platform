"""Tests for model_providers factory module."""

from unittest.mock import MagicMock

import pytest

from job_agent_backend.model_providers.factory import ModelFactory
from job_agent_backend.model_providers.config import _registry


class TestModelFactoryGenerateCacheKey:
    """Tests for ModelFactory._generate_cache_key method."""

    def test_generates_key_from_parameters(self) -> None:
        factory = ModelFactory()

        key = factory._generate_cache_key("openai", "gpt-4", 0.5, {})

        assert key == "openai:gpt-4:temp=0.5:"

    def test_includes_sorted_kwargs_in_key(self) -> None:
        factory = ModelFactory()

        key = factory._generate_cache_key("openai", "gpt-4", 0.0, {"b": 2, "a": 1})

        assert key == "openai:gpt-4:temp=0.0:a=1_b=2"

    def test_generates_consistent_keys_for_same_parameters(self) -> None:
        factory = ModelFactory()

        key1 = factory._generate_cache_key("openai", "gpt-4", 0.5, {"x": 1})
        key2 = factory._generate_cache_key("openai", "gpt-4", 0.5, {"x": 1})

        assert key1 == key2


class TestModelFactoryGetModel:
    """Tests for ModelFactory.get_model method."""

    def test_raises_error_when_no_model_id_or_model_name(self) -> None:
        factory = ModelFactory()

        with pytest.raises(ValueError, match="Either 'model_id' or 'model_name' must be provided"):
            factory.get_model()

    def test_raises_error_for_unknown_model_id(self) -> None:
        factory = ModelFactory()

        with pytest.raises(ValueError, match="not found"):
            factory.get_model(model_id="nonexistent-model")

    def test_raises_error_for_unknown_model_name_without_provider(self) -> None:
        factory = ModelFactory()

        with pytest.raises(ValueError, match="Cannot auto-detect provider"):
            factory.get_model(model_name="unknown-model-xyz")

    def test_raises_error_for_unsupported_provider(self) -> None:
        factory = ModelFactory()

        with pytest.raises(ValueError, match="Unsupported provider"):
            factory.get_model(provider="unsupported", model_name="some-model")

    def test_creates_model_with_explicit_provider_and_model_name(self) -> None:
        factory = ModelFactory()
        mock_model = MagicMock()
        mock_provider_instance = MagicMock()
        mock_provider_instance.get_model.return_value = mock_model
        mock_provider_class = MagicMock(return_value=mock_provider_instance)

        factory.PROVIDER_MAP = {"openai": mock_provider_class}
        result = factory.get_model(provider="openai", model_name="gpt-4", api_key="test-key")

        assert result == mock_model
        mock_provider_class.assert_called_once_with(
            model_name="gpt-4", temperature=0.0, api_key="test-key"
        )

    def test_creates_model_with_auto_detected_provider(self) -> None:
        factory = ModelFactory()
        mock_model = MagicMock()
        mock_provider_instance = MagicMock()
        mock_provider_instance.get_model.return_value = mock_model
        mock_provider_class = MagicMock(return_value=mock_provider_instance)

        factory.PROVIDER_MAP = {"openai": mock_provider_class}
        result = factory.get_model(model_name="gpt-4o-mini", api_key="test-key")

        assert result == mock_model
        mock_provider_class.assert_called_once()

    def test_creates_model_from_registered_provider(self) -> None:
        factory = ModelFactory()
        mock_model = MagicMock()
        mock_provider = MagicMock()
        mock_provider.get_model.return_value = mock_model
        original_providers = _registry._providers.copy()

        try:
            _registry._providers["test-registered"] = mock_provider

            result = factory.get_model(model_id="test-registered")

            assert result == mock_model
            mock_provider.get_model.assert_called_once()
        finally:
            _registry._providers = original_providers

    def test_handles_case_insensitive_provider(self) -> None:
        factory = ModelFactory()
        mock_model = MagicMock()
        mock_provider_instance = MagicMock()
        mock_provider_instance.get_model.return_value = mock_model
        mock_provider_class = MagicMock(return_value=mock_provider_instance)

        factory.PROVIDER_MAP = {"openai": mock_provider_class}
        result = factory.get_model(provider="OPENAI", model_name="gpt-4", api_key="test-key")

        assert result == mock_model


class TestModelFactoryCaching:
    """Tests for ModelFactory caching behavior."""

    def test_returns_cached_model_on_second_call(self) -> None:
        factory = ModelFactory()
        mock_model = MagicMock()
        call_count = 0

        def create_provider(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_instance = MagicMock()
            mock_instance.get_model.return_value = mock_model
            return mock_instance

        mock_provider_class = MagicMock(side_effect=create_provider)
        factory.PROVIDER_MAP = {"openai": mock_provider_class}

        result1 = factory.get_model(provider="openai", model_name="gpt-4", api_key="key")
        result2 = factory.get_model(provider="openai", model_name="gpt-4", api_key="key")

        assert result1 is result2
        assert call_count == 1

    def test_creates_new_model_for_different_parameters(self) -> None:
        factory = ModelFactory()
        mock_model1 = MagicMock()
        mock_model2 = MagicMock()
        models = [mock_model1, mock_model2]
        call_count = 0

        def create_provider(*args, **kwargs):
            nonlocal call_count
            mock_instance = MagicMock()
            mock_instance.get_model.return_value = models[call_count]
            call_count += 1
            return mock_instance

        mock_provider_class = MagicMock(side_effect=create_provider)
        factory.PROVIDER_MAP = {"openai": mock_provider_class}

        result1 = factory.get_model(
            provider="openai", model_name="gpt-4", temperature=0.0, api_key="key"
        )
        result2 = factory.get_model(
            provider="openai", model_name="gpt-4", temperature=0.5, api_key="key"
        )

        assert result1 is not result2
        assert call_count == 2

    def test_get_cache_size_returns_number_of_cached_models(self) -> None:
        factory = ModelFactory()
        mock_model = MagicMock()

        def create_provider(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.get_model.return_value = mock_model
            return mock_instance

        mock_provider_class = MagicMock(side_effect=create_provider)
        factory.PROVIDER_MAP = {"openai": mock_provider_class}

        assert factory.get_cache_size() == 0

        factory.get_model(provider="openai", model_name="gpt-4", api_key="key")
        assert factory.get_cache_size() == 1

        factory.get_model(provider="openai", model_name="gpt-4", temperature=0.5, api_key="key")
        assert factory.get_cache_size() == 2

    def test_clear_cache_removes_all_cached_models(self) -> None:
        factory = ModelFactory()
        mock_model = MagicMock()

        def create_provider(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.get_model.return_value = mock_model
            return mock_instance

        mock_provider_class = MagicMock(side_effect=create_provider)
        factory.PROVIDER_MAP = {"openai": mock_provider_class}

        factory.get_model(provider="openai", model_name="gpt-4", api_key="key")
        factory.get_model(provider="openai", model_name="gpt-4", temperature=0.5, api_key="key")
        assert factory.get_cache_size() == 2

        factory.clear_cache()

        assert factory.get_cache_size() == 0

    def test_caches_registered_models(self) -> None:
        factory = ModelFactory()
        mock_model = MagicMock()
        mock_provider = MagicMock()
        mock_provider.get_model.return_value = mock_model
        original_providers = _registry._providers.copy()

        try:
            _registry._providers["cached-test"] = mock_provider

            result1 = factory.get_model(model_id="cached-test")
            result2 = factory.get_model(model_id="cached-test")

            assert result1 is result2
            mock_provider.get_model.assert_called_once()
        finally:
            _registry._providers = original_providers
