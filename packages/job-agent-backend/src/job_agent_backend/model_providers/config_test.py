"""Tests for model_providers config module."""

from unittest.mock import MagicMock

from job_agent_backend.model_providers.config import ModelRegistry


class TestModelRegistry:
    """Tests for ModelRegistry class."""

    def test_initializes_with_providers_list(self) -> None:
        provider1 = MagicMock()
        provider2 = MagicMock()

        registry = ModelRegistry([
            ("model1", provider1),
            ("model2", provider2),
        ])

        assert len(registry._providers) == 2
        assert registry._providers["model1"] == provider1
        assert registry._providers["model2"] == provider2

    def test_initializes_with_empty_list(self) -> None:
        registry = ModelRegistry([])

        assert len(registry._providers) == 0

    def test_get_returns_provider(self) -> None:
        provider = MagicMock()
        registry = ModelRegistry([("my-model", provider)])

        result = registry.get("my-model")

        assert result == provider

    def test_get_returns_none_for_unknown_model(self) -> None:
        registry = ModelRegistry([])

        result = registry.get("unknown-model")

        assert result is None

    def test_get_model_returns_model_instance(self) -> None:
        mock_model = MagicMock()
        provider = MagicMock()
        provider.get_model.return_value = mock_model
        registry = ModelRegistry([("my-model", provider)])

        result = registry.get_model("my-model")

        assert result == mock_model
        provider.get_model.assert_called_once()

    def test_get_model_raises_for_unknown_model(self) -> None:
        registry = ModelRegistry([])

        try:
            registry.get_model("unknown")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "not found" in str(e)

    def test_list_models_returns_all_ids(self) -> None:
        registry = ModelRegistry([
            ("model1", MagicMock()),
            ("model2", MagicMock()),
        ])

        result = registry.list_models()

        assert set(result) == {"model1", "model2"}
