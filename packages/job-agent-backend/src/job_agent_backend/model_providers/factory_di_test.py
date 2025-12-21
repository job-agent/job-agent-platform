"""Tests for ModelFactory dependency injection (REQ-8, REQ-9, REQ-10, REQ-11).

These tests verify that ModelFactory accepts injected dependencies
instead of using module-level singletons and class-level attributes.
"""

from typing import Dict, Type
from unittest.mock import MagicMock

import pytest

from job_agent_backend.model_providers.providers import IModelProvider


class TestModelFactoryConstructorAcceptsRegistry:
    """Tests for REQ-8: ModelFactory constructor accepts IModelRegistry."""

    def test_constructor_accepts_registry_parameter(self) -> None:
        """REQ-8: ModelFactory.__init__ accepts registry parameter."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.registry_interface import IModelRegistry

        mock_registry = MagicMock(spec=IModelRegistry)
        mock_provider_map: Dict[str, Type[IModelProvider]] = {}

        factory = ModelFactory(registry=mock_registry, provider_map=mock_provider_map)

        assert factory is not None

    def test_factory_uses_injected_registry_for_model_id_lookup(self) -> None:
        """REQ-8: ModelFactory uses injected registry for model_id lookups."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.registry_interface import IModelRegistry

        mock_model = MagicMock()
        mock_provider = MagicMock(spec=IModelProvider)
        mock_provider.get_model.return_value = mock_model

        mock_registry = MagicMock(spec=IModelRegistry)
        mock_registry.get.return_value = mock_provider
        mock_registry.list_models.return_value = ["test-model"]

        mock_provider_map: Dict[str, Type[IModelProvider]] = {}

        factory = ModelFactory(registry=mock_registry, provider_map=mock_provider_map)
        result = factory.get_model(model_id="test-model")

        assert result == mock_model
        mock_registry.get.assert_called_once_with("test-model")

    def test_factory_raises_error_when_model_id_not_in_registry(self) -> None:
        """REQ-8: Error when model_id not found in injected registry."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.registry_interface import IModelRegistry

        mock_registry = MagicMock(spec=IModelRegistry)
        mock_registry.get.return_value = None
        mock_registry.list_models.return_value = []

        mock_provider_map: Dict[str, Type[IModelProvider]] = {}

        factory = ModelFactory(registry=mock_registry, provider_map=mock_provider_map)

        with pytest.raises(ValueError, match="not found"):
            factory.get_model(model_id="nonexistent-model")


class TestModelFactoryConstructorAcceptsProviderMap:
    """Tests for REQ-9: ModelFactory constructor accepts provider_map."""

    def test_constructor_accepts_provider_map_parameter(self) -> None:
        """REQ-9: ModelFactory.__init__ accepts provider_map parameter."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.registry_interface import IModelRegistry

        mock_registry = MagicMock(spec=IModelRegistry)
        mock_provider_map = {"openai": MagicMock}

        factory = ModelFactory(registry=mock_registry, provider_map=mock_provider_map)

        assert factory is not None

    def test_factory_uses_injected_provider_map_for_on_the_fly_creation(self) -> None:
        """REQ-9: ModelFactory uses injected provider_map for on-the-fly creation."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.registry_interface import IModelRegistry

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
        """REQ-9: Error when provider not in injected provider_map."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.registry_interface import IModelRegistry

        mock_registry = MagicMock(spec=IModelRegistry)
        mock_provider_map: Dict[str, Type[IModelProvider]] = {}

        factory = ModelFactory(registry=mock_registry, provider_map=mock_provider_map)

        with pytest.raises(ValueError, match="Unsupported provider"):
            factory.get_model(provider="unsupported", model_name="some-model")


class TestModelFactoryConstructorAcceptsModelProviderMap:
    """Tests for REQ-10: ModelFactory constructor accepts optional model_provider_map."""

    def test_constructor_accepts_optional_model_provider_map(self) -> None:
        """REQ-10: ModelFactory.__init__ accepts model_provider_map parameter."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.registry_interface import IModelRegistry

        mock_registry = MagicMock(spec=IModelRegistry)
        mock_provider_map: Dict[str, Type[IModelProvider]] = {}
        custom_model_map = {"custom-model": "custom-provider"}

        factory = ModelFactory(
            registry=mock_registry,
            provider_map=mock_provider_map,
            model_provider_map=custom_model_map,
        )

        assert factory is not None

    def test_model_provider_map_defaults_to_standard_map(self) -> None:
        """REQ-10: model_provider_map defaults to MODEL_PROVIDER_MAP when not provided."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.registry_interface import IModelRegistry

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
        """REQ-10: Factory uses injected model_provider_map for provider auto-detection."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.registry_interface import IModelRegistry

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


class TestModelFactoryNoDirectProviderImports:
    """Tests for REQ-11: factory.py does not import provider classes directly."""

    def test_factory_module_has_no_openai_provider_import(self) -> None:
        """REQ-11: factory.py does not import OpenAIProvider directly."""
        import job_agent_backend.model_providers.factory as factory_module

        # Check module doesn't have direct reference to OpenAIProvider
        assert not hasattr(factory_module, "OpenAIProvider")

    def test_factory_module_has_no_ollama_provider_import(self) -> None:
        """REQ-11: factory.py does not import OllamaProvider directly."""
        import job_agent_backend.model_providers.factory as factory_module

        assert not hasattr(factory_module, "OllamaProvider")

    def test_factory_module_has_no_transformers_provider_import(self) -> None:
        """REQ-11: factory.py does not import TransformersProvider directly."""
        import job_agent_backend.model_providers.factory as factory_module

        assert not hasattr(factory_module, "TransformersProvider")

    def test_factory_class_has_no_provider_map_class_attribute(self) -> None:
        """REQ-11: ModelFactory does not have class-level PROVIDER_MAP."""
        from job_agent_backend.model_providers.factory import ModelFactory

        # PROVIDER_MAP should not be a class attribute - it's now injected
        assert not hasattr(ModelFactory, "PROVIDER_MAP")


class TestModelFactoryNoRegistrySingletonImport:
    """Tests for REQ-3: factory.py does not import _registry singleton."""

    def test_factory_module_has_no_registry_singleton_import(self) -> None:
        """REQ-3: factory.py does not import _registry from registry module."""
        import job_agent_backend.model_providers.factory as factory_module

        assert not hasattr(factory_module, "_registry")


class TestModelFactoryCachingWithDI:
    """Tests for caching behavior with dependency injection."""

    def test_caches_registered_models_with_injected_registry(self) -> None:
        """Caching works correctly with injected registry."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.registry_interface import IModelRegistry

        mock_model = MagicMock()
        mock_provider = MagicMock(spec=IModelProvider)
        mock_provider.get_model.return_value = mock_model

        mock_registry = MagicMock(spec=IModelRegistry)
        mock_registry.get.return_value = mock_provider
        mock_registry.list_models.return_value = ["cached-test"]

        mock_provider_map: Dict[str, Type[IModelProvider]] = {}

        factory = ModelFactory(registry=mock_registry, provider_map=mock_provider_map)

        result1 = factory.get_model(model_id="cached-test")
        result2 = factory.get_model(model_id="cached-test")

        assert result1 is result2
        # Provider's get_model should only be called once due to caching
        mock_provider.get_model.assert_called_once()

    def test_caches_on_the_fly_models_with_injected_provider_map(self) -> None:
        """Caching works correctly with injected provider_map."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.registry_interface import IModelRegistry

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
    """Tests for case-insensitive provider handling with DI."""

    def test_handles_case_insensitive_provider_with_injected_map(self) -> None:
        """Provider name is case-insensitive with injected provider_map."""
        from job_agent_backend.model_providers.factory import ModelFactory
        from job_agent_backend.model_providers.registry_interface import IModelRegistry

        mock_model = MagicMock()
        mock_provider_instance = MagicMock(spec=IModelProvider)
        mock_provider_instance.get_model.return_value = mock_model
        mock_provider_class = MagicMock(return_value=mock_provider_instance)

        mock_registry = MagicMock(spec=IModelRegistry)
        mock_provider_map = {"openai": mock_provider_class}

        factory = ModelFactory(registry=mock_registry, provider_map=mock_provider_map)
        result = factory.get_model(provider="OPENAI", model_name="gpt-4", api_key="test-key")

        assert result == mock_model
