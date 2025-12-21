"""Tests for PROVIDER_MAP in mappers directory (REQ-7)."""


class TestProviderMap:
    """Tests for PROVIDER_MAP dictionary mapping provider strings to classes."""

    def test_provider_map_is_importable(self) -> None:
        """PROVIDER_MAP is importable from mappers.provider_map."""
        from job_agent_backend.model_providers.mappers.provider_map import PROVIDER_MAP

        assert PROVIDER_MAP is not None

    def test_provider_map_is_dict(self) -> None:
        """PROVIDER_MAP is a dictionary."""
        from job_agent_backend.model_providers.mappers.provider_map import PROVIDER_MAP

        assert isinstance(PROVIDER_MAP, dict)

    def test_provider_map_contains_openai(self) -> None:
        """PROVIDER_MAP maps 'openai' to OpenAIProvider."""
        from job_agent_backend.model_providers.mappers.provider_map import PROVIDER_MAP
        from job_agent_backend.model_providers.providers import OpenAIProvider

        assert "openai" in PROVIDER_MAP
        assert PROVIDER_MAP["openai"] is OpenAIProvider

    def test_provider_map_contains_ollama(self) -> None:
        """PROVIDER_MAP maps 'ollama' to OllamaProvider."""
        from job_agent_backend.model_providers.mappers.provider_map import PROVIDER_MAP
        from job_agent_backend.model_providers.providers import OllamaProvider

        assert "ollama" in PROVIDER_MAP
        assert PROVIDER_MAP["ollama"] is OllamaProvider

    def test_provider_map_contains_transformers(self) -> None:
        """PROVIDER_MAP maps 'transformers' to TransformersProvider."""
        from job_agent_backend.model_providers.mappers.provider_map import PROVIDER_MAP
        from job_agent_backend.model_providers.providers import TransformersProvider

        assert "transformers" in PROVIDER_MAP
        assert PROVIDER_MAP["transformers"] is TransformersProvider

    def test_provider_map_values_are_types(self) -> None:
        """All PROVIDER_MAP values are class types (not instances)."""
        from job_agent_backend.model_providers.mappers.provider_map import PROVIDER_MAP

        for key, value in PROVIDER_MAP.items():
            assert isinstance(value, type), f"PROVIDER_MAP['{key}'] should be a class, not instance"

    def test_provider_map_values_implement_imodelprovider(self) -> None:
        """All provider classes implement IModelProvider interface."""
        from job_agent_backend.model_providers.mappers.provider_map import PROVIDER_MAP
        from job_agent_backend.model_providers.providers import IModelProvider

        for key, provider_class in PROVIDER_MAP.items():
            assert issubclass(
                provider_class, IModelProvider
            ), f"PROVIDER_MAP['{key}'] = {provider_class} should be subclass of IModelProvider"


class TestProviderMapExportedFromMappers:
    """Tests for PROVIDER_MAP export from mappers package."""

    def test_provider_map_exported_from_mappers_init(self) -> None:
        """PROVIDER_MAP is exported from mappers/__init__.py."""
        from job_agent_backend.model_providers.mappers import PROVIDER_MAP

        assert PROVIDER_MAP is not None
        assert isinstance(PROVIDER_MAP, dict)
