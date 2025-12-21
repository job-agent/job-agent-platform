"""Tests for container integration between ApplicationContainer and ModelProvidersContainer."""

import pytest


class TestModelProvidersContainerRegistry:
    """Tests for ModelProvidersContainer registry configuration."""

    def test_container_has_model_registry_provider(self) -> None:
        """ModelProvidersContainer provides model_registry."""
        from job_agent_backend.model_providers.container import ModelProvidersContainer

        container = ModelProvidersContainer()
        assert hasattr(container, "model_registry")

    def test_model_registry_is_configured_with_providers(self) -> None:
        """model_registry is configured with pre-configured providers."""
        from job_agent_backend.model_providers.container import container

        registry = container.model_registry()

        # Use class name check to avoid module caching issues in test runs
        assert type(registry).__name__ == "ModelRegistry"

    def test_model_registry_has_skill_extraction_model(self) -> None:
        """Registry has skill-extraction model configured."""
        from job_agent_backend.model_providers.container import container

        registry = container.model_registry()
        provider = registry.get("skill-extraction")

        assert provider is not None

    def test_model_registry_has_pii_removal_model(self) -> None:
        """Registry has pii-removal model configured."""
        from job_agent_backend.model_providers.container import container

        registry = container.model_registry()
        provider = registry.get("pii-removal")

        assert provider is not None

    def test_model_registry_has_embedding_model(self) -> None:
        """Registry has embedding model configured."""
        from job_agent_backend.model_providers.container import container

        registry = container.model_registry()
        provider = registry.get("embedding")

        assert provider is not None

    def test_pre_configured_models_list(self) -> None:
        """Registry lists all pre-configured models."""
        from job_agent_backend.model_providers.container import container

        registry = container.model_registry()
        models = registry.list_models()

        assert "skill-extraction" in models
        assert "pii-removal" in models
        assert "embedding" in models


class TestModelProvidersContainerGet:
    """Tests for ModelProvidersContainer get() function."""

    def test_get_imodel_registry_returns_model_registry(self) -> None:
        """get(IModelRegistry) returns configured ModelRegistry."""
        from job_agent_backend.model_providers.container import get
        from job_agent_backend.model_providers.contracts import IModelRegistry

        registry = get(IModelRegistry)

        # Use class name check to avoid module caching issues in test runs
        assert type(registry).__name__ == "ModelRegistry"

    def test_get_imodel_factory_returns_configured_factory(self) -> None:
        """get(IModelFactory) returns ModelFactory with injected dependencies."""
        from job_agent_backend.model_providers.container import get
        from job_agent_backend.model_providers import IModelFactory, ModelFactory

        factory = get(IModelFactory)

        assert isinstance(factory, ModelFactory)

    def test_get_unknown_type_raises_keyerror(self) -> None:
        """get() raises KeyError for unknown types."""
        from job_agent_backend.model_providers.container import get

        class UnknownType:
            pass

        with pytest.raises(KeyError) as exc_info:
            get(UnknownType)

        assert "UnknownType" in str(exc_info.value)


class TestModelProvidersContainerFactoryInjection:
    """Tests for ModelFactory injection in ModelProvidersContainer."""

    def test_model_factory_provider_accepts_registry(self) -> None:
        """model_factory provider is configured with registry."""
        from job_agent_backend.model_providers.container import container
        from job_agent_backend.model_providers.factory import ModelFactory

        factory = container.model_factory()

        assert isinstance(factory, ModelFactory)

    def test_model_factory_can_resolve_pre_configured_models(self) -> None:
        """ModelFactory can get models by model_id via injected registry."""
        from job_agent_backend.model_providers.container import container

        factory = container.model_factory()

        # This should not raise an error - the registry should have the model
        try:
            result = factory.get_model(model_id="skill-extraction")
            assert result is not None
        except Exception as e:
            # If it fails for external reasons (network, API keys), that's ok
            # The important thing is it doesn't fail because registry is not injected
            if "not found" in str(e).lower():
                pytest.fail(
                    f"Model 'skill-extraction' not found - registry not properly injected: {e}"
                )

    def test_model_factory_uses_injected_provider_map(self) -> None:
        """ModelFactory uses PROVIDER_MAP from mappers via injection."""
        from job_agent_backend.model_providers.container import container
        from job_agent_backend.model_providers.mappers import PROVIDER_MAP

        factory = container.model_factory()

        # Verify factory accepts provider names from PROVIDER_MAP
        for provider_name in PROVIDER_MAP.keys():
            try:
                factory.get_model(provider=provider_name, model_name="test-model")
            except ValueError as e:
                # Should NOT see "Unsupported provider" error
                if "Unsupported provider" in str(e):
                    pytest.fail(f"Provider '{provider_name}' from PROVIDER_MAP is not recognized")
            except Exception:
                # Other errors are ok - we just want to verify provider is recognized
                pass


class TestApplicationContainerModelFactory:
    """Tests for ApplicationContainer model_factory integration."""

    def test_application_container_has_model_factory(self) -> None:
        """ApplicationContainer provides model_factory."""
        from job_agent_backend.container import ApplicationContainer

        container = ApplicationContainer()
        assert hasattr(container, "model_factory")

    def test_application_container_does_not_expose_model_registry(self) -> None:
        """ApplicationContainer does NOT expose model_registry directly."""
        from job_agent_backend.container import ApplicationContainer

        container = ApplicationContainer()
        assert not hasattr(container, "model_registry")

    def test_application_get_returns_model_factory(self) -> None:
        """Application get(IModelFactory) returns the same instance as model_providers."""
        from job_agent_backend.container import get as app_get
        from job_agent_backend.model_providers import IModelFactory
        from job_agent_backend.model_providers.container import get as mp_get

        app_factory = app_get(IModelFactory)
        mp_factory = mp_get(IModelFactory)

        # Both should return the same singleton instance
        assert app_factory is mp_factory

    def test_application_dependency_map_has_imodel_factory(self) -> None:
        """IModelFactory is in ApplicationContainer's _DEPENDENCY_MAP."""
        from job_agent_backend.container import _DEPENDENCY_MAP
        from job_agent_backend.model_providers import IModelFactory

        assert IModelFactory in _DEPENDENCY_MAP

    def test_application_dependency_map_does_not_have_imodel_registry(self) -> None:
        """IModelRegistry is NOT in ApplicationContainer's _DEPENDENCY_MAP."""
        from job_agent_backend.container import _DEPENDENCY_MAP
        from job_agent_backend.model_providers.contracts import IModelRegistry

        assert IModelRegistry not in _DEPENDENCY_MAP
