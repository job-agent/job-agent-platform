"""Tests for ModelProvidersContainer (REQ-4)."""


class TestModelProvidersContainerImport:
    """Tests that ModelProvidersContainer is properly importable."""

    def test_container_is_importable(self) -> None:
        """REQ-4: ModelProvidersContainer is importable from model_providers.container."""
        from job_agent_backend.model_providers.container import ModelProvidersContainer

        assert ModelProvidersContainer is not None

    def test_container_can_be_instantiated(self) -> None:
        """REQ-4: ModelProvidersContainer can be instantiated."""
        from job_agent_backend.model_providers.container import ModelProvidersContainer

        container = ModelProvidersContainer()
        assert container is not None


class TestModelProvidersContainerProviders:
    """Tests for providers defined in ModelProvidersContainer."""

    def test_container_has_provider_map_provider(self) -> None:
        """REQ-4: Container provides provider_map."""
        from job_agent_backend.model_providers.container import ModelProvidersContainer

        container = ModelProvidersContainer()
        assert hasattr(container, "provider_map")

    def test_provider_map_returns_expected_dictionary(self) -> None:
        """REQ-4: provider_map provider returns PROVIDER_MAP dictionary."""
        from job_agent_backend.model_providers.container import ModelProvidersContainer
        from job_agent_backend.model_providers.mappers import PROVIDER_MAP

        container = ModelProvidersContainer()
        result = container.provider_map()

        assert result == PROVIDER_MAP

    def test_container_has_model_provider_map_provider(self) -> None:
        """REQ-4: Container provides model_provider_map."""
        from job_agent_backend.model_providers.container import ModelProvidersContainer

        container = ModelProvidersContainer()
        assert hasattr(container, "model_provider_map")

    def test_model_provider_map_returns_expected_dictionary(self) -> None:
        """REQ-4: model_provider_map provider returns MODEL_PROVIDER_MAP dictionary."""
        from job_agent_backend.model_providers.container import ModelProvidersContainer
        from job_agent_backend.model_providers.mappers import MODEL_PROVIDER_MAP

        container = ModelProvidersContainer()
        result = container.model_provider_map()

        assert result == MODEL_PROVIDER_MAP

    def test_container_has_model_registry_provider(self) -> None:
        """REQ-4: Container provides model_registry singleton."""
        from job_agent_backend.model_providers.container import ModelProvidersContainer

        container = ModelProvidersContainer()
        assert hasattr(container, "model_registry")

    def test_model_registry_provider_returns_model_registry_instance(self) -> None:
        """REQ-4: model_registry provider returns ModelRegistry instance."""
        from job_agent_backend.model_providers.container import ModelProvidersContainer
        from job_agent_backend.model_providers.registry import ModelRegistry

        container = ModelProvidersContainer()
        result = container.model_registry()

        assert isinstance(result, ModelRegistry)

    def test_container_has_model_factory_provider(self) -> None:
        """REQ-4: Container provides model_factory factory."""
        from job_agent_backend.model_providers.container import ModelProvidersContainer

        container = ModelProvidersContainer()
        assert hasattr(container, "model_factory")

    def test_model_factory_provider_returns_model_factory_instance(self) -> None:
        """REQ-4: model_factory provider returns ModelFactory instance."""
        from job_agent_backend.model_providers.container import ModelProvidersContainer
        from job_agent_backend.model_providers.factory import ModelFactory

        container = ModelProvidersContainer()
        result = container.model_factory()

        assert isinstance(result, ModelFactory)


class TestModelProvidersContainerUsesDependencyInjector:
    """Tests that container uses dependency-injector library."""

    def test_container_is_declarative_container(self) -> None:
        """REQ-4: Container uses dependency-injector DeclarativeContainer."""
        from dependency_injector import containers

        from job_agent_backend.model_providers.container import ModelProvidersContainer

        assert issubclass(ModelProvidersContainer, containers.DeclarativeContainer)
