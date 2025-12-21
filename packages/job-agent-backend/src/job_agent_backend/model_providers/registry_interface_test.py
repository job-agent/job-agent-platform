"""Tests for IModelRegistry interface (REQ-1, REQ-2)."""

from abc import ABC
from unittest.mock import MagicMock

import pytest


class TestIModelRegistryInterface:
    """Tests for IModelRegistry abstract interface."""

    def test_interface_cannot_be_instantiated_directly(self) -> None:
        """REQ-1: IModelRegistry is an abstract base class."""
        from job_agent_backend.model_providers.registry_interface import IModelRegistry

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IModelRegistry()  # type: ignore

    def test_interface_inherits_from_abc(self) -> None:
        """REQ-1: IModelRegistry follows ABC pattern."""
        from job_agent_backend.model_providers.registry_interface import IModelRegistry

        assert issubclass(IModelRegistry, ABC)

    def test_interface_defines_get_method(self) -> None:
        """REQ-1: Interface defines get(model_id) -> Optional[IModelProvider]."""
        from job_agent_backend.model_providers.registry_interface import IModelRegistry

        assert hasattr(IModelRegistry, "get")
        assert callable(getattr(IModelRegistry, "get"))

    def test_interface_defines_get_model_method(self) -> None:
        """REQ-1: Interface defines get_model(model_id) -> Any."""
        from job_agent_backend.model_providers.registry_interface import IModelRegistry

        assert hasattr(IModelRegistry, "get_model")
        assert callable(getattr(IModelRegistry, "get_model"))

    def test_interface_defines_list_models_method(self) -> None:
        """REQ-1: Interface defines list_models() -> List[str]."""
        from job_agent_backend.model_providers.registry_interface import IModelRegistry

        assert hasattr(IModelRegistry, "list_models")
        assert callable(getattr(IModelRegistry, "list_models"))


class TestModelRegistryImplementsInterface:
    """Tests that ModelRegistry implements IModelRegistry (REQ-2)."""

    def test_model_registry_is_subclass_of_interface(self) -> None:
        """REQ-2: ModelRegistry inherits from IModelRegistry."""
        from job_agent_backend.model_providers.registry import ModelRegistry
        from job_agent_backend.model_providers.registry_interface import IModelRegistry

        assert issubclass(ModelRegistry, IModelRegistry)

    def test_model_registry_instance_is_interface_instance(self) -> None:
        """REQ-2: ModelRegistry instances are IModelRegistry instances."""
        from job_agent_backend.model_providers.registry import ModelRegistry
        from job_agent_backend.model_providers.registry_interface import IModelRegistry

        registry = ModelRegistry([])
        assert isinstance(registry, IModelRegistry)

    def test_model_registry_implements_get(self) -> None:
        """REQ-2: ModelRegistry.get() works correctly."""
        from job_agent_backend.model_providers.registry import ModelRegistry

        mock_provider = MagicMock()
        registry = ModelRegistry([("test-model", mock_provider)])

        result = registry.get("test-model")

        assert result == mock_provider

    def test_model_registry_get_returns_none_for_unknown_model(self) -> None:
        """REQ-2: ModelRegistry.get() returns None for unknown model."""
        from job_agent_backend.model_providers.registry import ModelRegistry

        registry = ModelRegistry([])

        result = registry.get("unknown-model")

        assert result is None

    def test_model_registry_implements_get_model(self) -> None:
        """REQ-2: ModelRegistry.get_model() works correctly."""
        from job_agent_backend.model_providers.registry import ModelRegistry

        mock_model = MagicMock()
        mock_provider = MagicMock()
        mock_provider.get_model.return_value = mock_model
        registry = ModelRegistry([("test-model", mock_provider)])

        result = registry.get_model("test-model")

        assert result == mock_model

    def test_model_registry_get_model_raises_for_unknown_model(self) -> None:
        """REQ-2: ModelRegistry.get_model() raises for unknown model."""
        from job_agent_backend.model_providers.registry import ModelRegistry

        registry = ModelRegistry([])

        with pytest.raises(ValueError, match="not found"):
            registry.get_model("unknown")

    def test_model_registry_implements_list_models(self) -> None:
        """REQ-2: ModelRegistry.list_models() works correctly."""
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
        """REQ-1: IModelRegistry is importable from model_providers package."""
        from job_agent_backend.model_providers import IModelRegistry

        assert IModelRegistry is not None

    def test_model_registry_exported_from_model_providers(self) -> None:
        """REQ-2: ModelRegistry is importable from model_providers package."""
        from job_agent_backend.model_providers import ModelRegistry

        assert ModelRegistry is not None
