"""Tests for IModelRegistry interface."""

from unittest.mock import MagicMock

import pytest


class TestModelRegistryImplementsInterface:
    """Tests that ModelRegistry implements IModelRegistry."""

    def test_model_registry_is_subclass_of_interface(self) -> None:
        """ModelRegistry inherits from IModelRegistry."""
        from job_agent_backend.model_providers.registry import ModelRegistry
        from job_agent_backend.model_providers.contracts import IModelRegistry

        assert issubclass(ModelRegistry, IModelRegistry)

    def test_model_registry_instance_is_interface_instance(self) -> None:
        """ModelRegistry instances are IModelRegistry instances."""
        from job_agent_backend.model_providers.registry import ModelRegistry
        from job_agent_backend.model_providers.contracts import IModelRegistry

        registry = ModelRegistry([])
        assert isinstance(registry, IModelRegistry)

    def test_model_registry_implements_get(self) -> None:
        """ModelRegistry.get() works correctly."""
        from job_agent_backend.model_providers.registry import ModelRegistry

        mock_provider = MagicMock()
        registry = ModelRegistry([("test-model", mock_provider)])

        result = registry.get("test-model")

        assert result == mock_provider

    def test_model_registry_get_returns_none_for_unknown_model(self) -> None:
        """ModelRegistry.get() returns None for unknown model."""
        from job_agent_backend.model_providers.registry import ModelRegistry

        registry = ModelRegistry([])

        result = registry.get("unknown-model")

        assert result is None

    def test_model_registry_implements_get_model(self) -> None:
        """ModelRegistry.get_model() works correctly."""
        from job_agent_backend.model_providers.registry import ModelRegistry

        mock_model = MagicMock()
        mock_provider = MagicMock()
        mock_provider.get_model.return_value = mock_model
        registry = ModelRegistry([("test-model", mock_provider)])

        result = registry.get_model("test-model")

        assert result == mock_model

    def test_model_registry_get_model_raises_for_unknown_model(self) -> None:
        """ModelRegistry.get_model() raises for unknown model."""
        from job_agent_backend.model_providers.registry import ModelRegistry

        registry = ModelRegistry([])

        with pytest.raises(ValueError, match="not found"):
            registry.get_model("unknown")

    def test_model_registry_implements_list_models(self) -> None:
        """ModelRegistry.list_models() works correctly."""
        from job_agent_backend.model_providers.registry import ModelRegistry

        registry = ModelRegistry(
            [
                ("model1", MagicMock()),
                ("model2", MagicMock()),
            ]
        )

        result = registry.list_models()

        assert set(result) == {"model1", "model2"}


class TestIModelRegistryExportedFromPackage:
    """Tests that IModelRegistry is properly exported."""

    def test_interface_exported_from_model_providers(self) -> None:
        """IModelRegistry is importable from model_providers package."""
        from job_agent_backend.model_providers import IModelRegistry

        assert IModelRegistry is not None

    def test_model_registry_exported_from_model_providers(self) -> None:
        """ModelRegistry is importable from model_providers package."""
        from job_agent_backend.model_providers import ModelRegistry

        assert ModelRegistry is not None
