"""Tests for MODEL_PROVIDER_MAP in mappers directory (REQ-6)."""


class TestModelProviderMapRelocation:
    """Tests that MODEL_PROVIDER_MAP is correctly relocated to mappers directory."""

    def test_model_provider_map_is_dict(self) -> None:
        """MODEL_PROVIDER_MAP is a dictionary."""
        from job_agent_backend.model_providers.mappers.model_provider_map import (
            MODEL_PROVIDER_MAP,
        )

        assert isinstance(MODEL_PROVIDER_MAP, dict)

    def test_model_provider_map_contains_gpt_4o_mini(self) -> None:
        """MODEL_PROVIDER_MAP contains gpt-4o-mini -> openai mapping."""
        from job_agent_backend.model_providers.mappers.model_provider_map import (
            MODEL_PROVIDER_MAP,
        )

        assert "gpt-4o-mini" in MODEL_PROVIDER_MAP
        assert MODEL_PROVIDER_MAP["gpt-4o-mini"] == "openai"

    def test_model_provider_map_contains_phi3_mini(self) -> None:
        """MODEL_PROVIDER_MAP contains phi3:mini -> ollama mapping."""
        from job_agent_backend.model_providers.mappers.model_provider_map import (
            MODEL_PROVIDER_MAP,
        )

        assert "phi3:mini" in MODEL_PROVIDER_MAP
        assert MODEL_PROVIDER_MAP["phi3:mini"] == "ollama"

    def test_model_provider_map_contains_transformers_model(self) -> None:
        """MODEL_PROVIDER_MAP contains sentence-transformers model."""
        from job_agent_backend.model_providers.mappers.model_provider_map import (
            MODEL_PROVIDER_MAP,
        )

        model_name = "sentence-transformers/distiluse-base-multilingual-cased-v2"
        assert model_name in MODEL_PROVIDER_MAP
        assert MODEL_PROVIDER_MAP[model_name] == "transformers"
