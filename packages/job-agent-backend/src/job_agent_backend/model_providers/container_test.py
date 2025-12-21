"""Tests for ModelProvidersContainer (REQ-4)."""


class TestModelProvidersContainerProviders:
    """Providers defined in ModelProvidersContainer."""

    def test_provider_map_returns_expected_dictionary(self) -> None:
        """Provider_map provider returns PROVIDER_MAP dictionary."""
        from job_agent_backend.model_providers.container import ModelProvidersContainer
        from job_agent_backend.model_providers.mappers import PROVIDER_MAP

        container = ModelProvidersContainer()
        result = container.provider_map()

        assert result == PROVIDER_MAP

    def test_model_provider_map_returns_expected_dictionary(self) -> None:
        """Model_provider_map provider returns MODEL_PROVIDER_MAP dictionary."""
        from job_agent_backend.model_providers.container import ModelProvidersContainer
        from job_agent_backend.model_providers.mappers import MODEL_PROVIDER_MAP

        container = ModelProvidersContainer()
        result = container.model_provider_map()

        assert result == MODEL_PROVIDER_MAP

    def test_model_registry_provider_returns_model_registry_instance(self) -> None:
        """Model_registry provider returns ModelRegistry instance."""
        from job_agent_backend.model_providers.container import ModelProvidersContainer
        from job_agent_backend.model_providers.registry import ModelRegistry

        container = ModelProvidersContainer()
        result = container.model_registry()

        assert isinstance(result, ModelRegistry)

    def test_model_factory_provider_returns_model_factory_instance(self) -> None:
        """Model_factory provider returns ModelFactory instance."""
        from job_agent_backend.model_providers.container import ModelProvidersContainer
        from job_agent_backend.model_providers.factory import ModelFactory

        container = ModelProvidersContainer()
        result = container.model_factory()

        assert isinstance(result, ModelFactory)
