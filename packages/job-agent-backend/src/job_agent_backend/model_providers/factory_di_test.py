"""ModelFactory dependency injection.

These tests verify that ModelFactory accepts injected dependencies
instead of using module-level singletons and class-level attributes.
"""

from typing import Dict, Type
from unittest.mock import MagicMock

import pytest

from job_agent_backend.model_providers.providers import IModelProvider
from job_agent_backend.model_providers.providers.base import BaseModelProvider


class TestModelFactoryConstructorAcceptsRegistry:
    """ModelFactory constructor accepts IModelRegistry."""

    def test_constructor_accepts_registry_parameter(self) -> None:
        """ModelFactory.__init__ accepts registry parameter."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.contracts import IModelRegistry

        mock_registry = MagicMock(spec=IModelRegistry)
        mock_provider_map: Dict[str, Type[BaseModelProvider]] = {}

        factory = ModelFactory(registry=mock_registry, provider_map=mock_provider_map)

        assert factory is not None

    def test_factory_uses_injected_registry_for_model_id_lookup(self) -> None:
        """ModelFactory uses injected registry for model_id lookups."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.contracts import IModelRegistry

        mock_model = MagicMock()
        mock_provider = MagicMock(spec=IModelProvider)
        mock_provider.get_model.return_value = mock_model

        mock_registry = MagicMock(spec=IModelRegistry)
        mock_registry.get.return_value = mock_provider
        mock_registry.list_models.return_value = ["test-model"]

        mock_provider_map: Dict[str, Type[BaseModelProvider]] = {}

        factory = ModelFactory(registry=mock_registry, provider_map=mock_provider_map)
        result = factory.get_model(model_id="test-model")

        assert result == mock_model
        mock_registry.get.assert_called_once_with("test-model")

    def test_factory_raises_error_when_model_id_not_in_registry(self) -> None:
        """Error when model_id not found in injected registry."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.contracts import IModelRegistry

        mock_registry = MagicMock(spec=IModelRegistry)
        mock_registry.get.return_value = None
        mock_registry.list_models.return_value = []

        mock_provider_map: Dict[str, Type[BaseModelProvider]] = {}

        factory = ModelFactory(registry=mock_registry, provider_map=mock_provider_map)

        with pytest.raises(ValueError, match="not found"):
            factory.get_model(model_id="nonexistent-model")


class TestModelFactoryConstructorAcceptsProviderMap:
    """ModelFactory constructor accepts provider_map."""

    def test_constructor_accepts_provider_map_parameter(self) -> None:
        """ModelFactory.__init__ accepts provider_map parameter."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.contracts import IModelRegistry

        mock_registry = MagicMock(spec=IModelRegistry)
        mock_provider_map = {"openai": MagicMock}

        factory = ModelFactory(registry=mock_registry, provider_map=mock_provider_map)

        assert factory is not None

    def test_factory_uses_injected_provider_map_for_on_the_fly_creation(self) -> None:
        """ModelFactory uses injected provider_map for on-the-fly creation."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.contracts import IModelRegistry

        mock_model = MagicMock()
        mock_provider_instance = MagicMock(spec=IModelProvider)
        mock_provider_instance.get_model.return_value = mock_model
        mock_provider_class = MagicMock(return_value=mock_provider_instance)

        mock_registry = MagicMock(spec=IModelRegistry)
        mock_provider_map = {"openai": mock_provider_class}

        factory = ModelFactory(registry=mock_registry, provider_map=mock_provider_map)
        result = factory.get_model(provider="openai", model_name="gpt-4", api_key="test-key")

        assert result == mock_model
        mock_provider_class.assert_called_once()

    def test_factory_raises_error_when_provider_not_in_map(self) -> None:
        """Error when provider not in injected provider_map."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.contracts import IModelRegistry

        mock_registry = MagicMock(spec=IModelRegistry)
        mock_provider_map: Dict[str, Type[BaseModelProvider]] = {}

        factory = ModelFactory(registry=mock_registry, provider_map=mock_provider_map)

        with pytest.raises(ValueError, match="Unsupported provider"):
            factory.get_model(provider="unsupported", model_name="some-model")


class TestModelFactoryConstructorAcceptsModelProviderMap:
    """ModelFactory constructor accepts optional model_provider_map."""

    def test_constructor_accepts_optional_model_provider_map(self) -> None:
        """ModelFactory.__init__ accepts model_provider_map parameter."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.contracts import IModelRegistry

        mock_registry = MagicMock(spec=IModelRegistry)
        mock_provider_map: Dict[str, Type[BaseModelProvider]] = {}
        custom_model_map = {"custom-model": "custom-provider"}

        factory = ModelFactory(
            registry=mock_registry,
            provider_map=mock_provider_map,
            model_provider_map=custom_model_map,
        )

        assert factory is not None

    def test_model_provider_map_defaults_to_standard_map(self) -> None:
        """model_provider_map defaults to MODEL_PROVIDER_MAP when not provided."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.contracts import IModelRegistry

        mock_model = MagicMock()
        mock_provider_instance = MagicMock(spec=IModelProvider)
        mock_provider_instance.get_model.return_value = mock_model
        mock_provider_class = MagicMock(return_value=mock_provider_instance)

        mock_registry = MagicMock(spec=IModelRegistry)
        mock_provider_map = {"openai": mock_provider_class}

        factory = ModelFactory(registry=mock_registry, provider_map=mock_provider_map)

        # gpt-4o-mini should auto-detect to openai based on MODEL_PROVIDER_MAP
        result = factory.get_model(model_name="gpt-4o-mini", api_key="test-key")

        assert result == mock_model
        mock_provider_class.assert_called_once()

    def test_factory_uses_injected_model_provider_map_for_auto_detection(self) -> None:
        """Factory uses injected model_provider_map for provider auto-detection."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.contracts import IModelRegistry

        mock_model = MagicMock()
        mock_provider_instance = MagicMock(spec=IModelProvider)
        mock_provider_instance.get_model.return_value = mock_model
        mock_provider_class = MagicMock(return_value=mock_provider_instance)

        mock_registry = MagicMock(spec=IModelRegistry)
        mock_provider_map = {"custom-provider": mock_provider_class}
        custom_model_map = {"custom-model-name": "custom-provider"}

        factory = ModelFactory(
            registry=mock_registry,
            provider_map=mock_provider_map,
            model_provider_map=custom_model_map,
        )

        result = factory.get_model(model_name="custom-model-name")

        assert result == mock_model
        mock_provider_class.assert_called_once()


class TestModelFactoryCachingWithDI:
    """caching behavior with dependency injection."""

    def test_caches_registered_models_with_injected_registry(self) -> None:
        """Caching works correctly with injected registry."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.contracts import IModelRegistry

        mock_model = MagicMock()
        mock_provider = MagicMock(spec=IModelProvider)
        mock_provider.get_model.return_value = mock_model

        mock_registry = MagicMock(spec=IModelRegistry)
        mock_registry.get.return_value = mock_provider
        mock_registry.list_models.return_value = ["cached-test"]

        mock_provider_map: Dict[str, Type[BaseModelProvider]] = {}

        factory = ModelFactory(registry=mock_registry, provider_map=mock_provider_map)

        result1 = factory.get_model(model_id="cached-test")
        result2 = factory.get_model(model_id="cached-test")

        assert result1 is result2
        # Provider's get_model should only be called once due to caching
        mock_provider.get_model.assert_called_once()

    def test_caches_on_the_fly_models_with_injected_provider_map(self) -> None:
        """Caching works correctly with injected provider_map."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.contracts import IModelRegistry

        mock_model = MagicMock()
        call_count = 0

        def create_provider(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            instance = MagicMock(spec=IModelProvider)
            instance.get_model.return_value = mock_model
            return instance

        mock_provider_class = MagicMock(side_effect=create_provider)
        mock_registry = MagicMock(spec=IModelRegistry)
        mock_provider_map = {"openai": mock_provider_class}

        factory = ModelFactory(registry=mock_registry, provider_map=mock_provider_map)

        result1 = factory.get_model(provider="openai", model_name="gpt-4", api_key="key")
        result2 = factory.get_model(provider="openai", model_name="gpt-4", api_key="key")

        assert result1 is result2
        assert call_count == 1


class TestModelFactoryHandlesCaseInsensitiveProviderWithDI:
    """case-insensitive provider handling with DI."""

    def test_handles_case_insensitive_provider_with_injected_map(self) -> None:
        """Provider name is case-insensitive with injected provider_map."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.contracts import IModelRegistry

        mock_model = MagicMock()
        mock_provider_instance = MagicMock(spec=IModelProvider)
        mock_provider_instance.get_model.return_value = mock_model
        mock_provider_class = MagicMock(return_value=mock_provider_instance)

        mock_registry = MagicMock(spec=IModelRegistry)
        mock_provider_map = {"openai": mock_provider_class}

        factory = ModelFactory(registry=mock_registry, provider_map=mock_provider_map)
        result = factory.get_model(provider="OPENAI", model_name="gpt-4", api_key="test-key")

        assert result == mock_model
