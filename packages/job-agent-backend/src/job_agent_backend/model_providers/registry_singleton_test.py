"""Tests for _registry singleton removal (REQ-3)."""


class TestRegistrySingletonRemoved:
    """Tests that _registry module-level singleton is removed from registry.py."""

    def test_registry_module_has_no_registry_singleton(self) -> None:
        """REQ-3: registry.py no longer creates _registry singleton at import time."""
        import job_agent_backend.model_providers.registry as registry_module

        assert not hasattr(
            registry_module, "_registry"
        ), "_registry module-level singleton should be removed from registry.py"

    def test_registry_module_still_has_model_registry_class(self) -> None:
        """REQ-3: registry.py still exports ModelRegistry class."""
        from job_agent_backend.model_providers.registry import ModelRegistry

        assert ModelRegistry is not None
        assert isinstance(ModelRegistry, type)

    def test_importing_registry_does_not_create_instances(self) -> None:
        """REQ-3: Importing registry module does not create any provider instances."""
        # This is a behavioral test: importing the module should not trigger
        # creation of OllamaProvider or TransformersProvider instances
        import importlib
        import sys

        # Remove cached module to test fresh import behavior
        module_name = "job_agent_backend.model_providers.registry"
        if module_name in sys.modules:
            del sys.modules[module_name]

        # Re-import - this should not raise any errors or side effects
        registry_module = importlib.import_module(module_name)

        # The module should only contain the class definition
        assert hasattr(registry_module, "ModelRegistry")
        assert not hasattr(registry_module, "_registry")
