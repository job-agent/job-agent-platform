"""Tests for model_providers config module."""

import os
from unittest.mock import patch


from job_agent_backend.model_providers.config import (
    ModelConfig,
    ModelRegistry,
    register_model,
    get_model_config,
    list_available_models,
    _registry,
)


class TestModelConfig:
    """Tests for ModelConfig dataclass."""

    def test_creates_config_with_required_fields(self) -> None:
        config = ModelConfig(
            model_id="test-model",
            provider="openai",
            model_name="gpt-4",
        )

        assert config.model_id == "test-model"
        assert config.provider == "openai"
        assert config.model_name == "gpt-4"
        assert config.temperature == 0.0
        assert config.kwargs == {}

    def test_creates_config_with_all_fields(self) -> None:
        config = ModelConfig(
            model_id="test-model",
            provider="openai",
            model_name="gpt-4",
            temperature=0.7,
            kwargs={"max_tokens": 100},
        )

        assert config.model_id == "test-model"
        assert config.provider == "openai"
        assert config.model_name == "gpt-4"
        assert config.temperature == 0.7
        assert config.kwargs == {"max_tokens": 100}


class TestModelRegistry:
    """Tests for ModelRegistry class."""

    def test_register_stores_config(self) -> None:
        registry = ModelRegistry.__new__(ModelRegistry)
        registry._models = {}

        config = ModelConfig(
            model_id="my-model",
            provider="openai",
            model_name="gpt-4",
        )
        registry.register(config)

        assert "my-model" in registry._models
        assert registry._models["my-model"] == config

    def test_get_returns_registered_config(self) -> None:
        registry = ModelRegistry.__new__(ModelRegistry)
        registry._models = {}

        config = ModelConfig(
            model_id="my-model",
            provider="openai",
            model_name="gpt-4",
        )
        registry.register(config)

        result = registry.get("my-model")

        assert result == config

    def test_get_returns_none_for_unknown_model(self) -> None:
        registry = ModelRegistry.__new__(ModelRegistry)
        registry._models = {}

        result = registry.get("unknown-model")

        assert result is None

    def test_list_models_returns_copy_of_all_configs(self) -> None:
        registry = ModelRegistry.__new__(ModelRegistry)
        registry._models = {}

        config1 = ModelConfig(model_id="model1", provider="openai", model_name="gpt-4")
        config2 = ModelConfig(model_id="model2", provider="ollama", model_name="phi3:mini")
        registry.register(config1)
        registry.register(config2)

        result = registry.list_models()

        assert len(result) == 2
        assert result["model1"] == config1
        assert result["model2"] == config2
        assert result is not registry._models

    def test_load_from_env_parses_model_configs(self) -> None:
        env_vars = {
            "MODEL_test_PROVIDER": "openai",
            "MODEL_test_MODEL_NAME": "gpt-4o-mini",
            "MODEL_test_TEMPERATURE": "0.5",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            registry = ModelRegistry()

        config = registry.get("test")
        assert config is not None
        assert config.provider == "openai"
        assert config.model_name == "gpt-4o-mini"
        assert config.temperature == 0.5

    def test_load_from_env_handles_model_id_with_underscores(self) -> None:
        env_vars = {
            "MODEL_skill_extraction_PROVIDER": "openai",
            "MODEL_skill_extraction_MODEL_NAME": "gpt-4",
            "MODEL_skill_extraction_TEMPERATURE": "0.0",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            registry = ModelRegistry()

        config = registry.get("skill_extraction")
        assert config is not None
        assert config.provider == "openai"
        assert config.model_name == "gpt-4"

    def test_load_from_env_collects_additional_kwargs(self) -> None:
        env_vars = {
            "MODEL_test_PROVIDER": "openai",
            "MODEL_test_MODEL_NAME": "gpt-4",
            "MODEL_test_TEMPERATURE": "0.0",
            "MODEL_test_MAX_TOKENS": "100",
            "MODEL_test_TOP_P": "0.9",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            registry = ModelRegistry()

        config = registry.get("test")
        assert config is not None
        assert config.kwargs == {"max_tokens": "100", "top_p": "0.9"}

    def test_load_from_env_skips_incomplete_configs(self) -> None:
        env_vars = {
            "MODEL_incomplete_PROVIDER": "openai",
            # Missing MODEL_NAME
        }

        with patch.dict(os.environ, env_vars, clear=True):
            registry = ModelRegistry()

        config = registry.get("incomplete")
        assert config is None

    def test_load_from_env_uses_default_temperature_for_invalid_value(self) -> None:
        env_vars = {
            "MODEL_test_PROVIDER": "openai",
            "MODEL_test_MODEL_NAME": "gpt-4",
            "MODEL_test_TEMPERATURE": "invalid",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            registry = ModelRegistry()

        config = registry.get("test")
        assert config is not None
        assert config.temperature == 0.0

    def test_load_from_env_normalizes_provider_to_lowercase(self) -> None:
        env_vars = {
            "MODEL_test_PROVIDER": "OpenAI",
            "MODEL_test_MODEL_NAME": "gpt-4",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            registry = ModelRegistry()

        config = registry.get("test")
        assert config is not None
        assert config.provider == "openai"


class TestRegisterModelFunction:
    """Tests for register_model helper function."""

    def test_registers_model_in_global_registry(self) -> None:
        original_models = _registry._models.copy()

        try:
            register_model(
                model_id="func-test-model",
                provider="openai",
                model_name="gpt-4",
                temperature=0.5,
            )

            config = _registry.get("func-test-model")
            assert config is not None
            assert config.provider == "openai"
            assert config.model_name == "gpt-4"
            assert config.temperature == 0.5
        finally:
            _registry._models = original_models

    def test_registers_model_with_kwargs(self) -> None:
        original_models = _registry._models.copy()

        try:
            register_model(
                model_id="func-test-kwargs",
                provider="openai",
                model_name="gpt-4",
                max_tokens=100,
                top_p=0.9,
            )

            config = _registry.get("func-test-kwargs")
            assert config is not None
            assert config.kwargs == {"max_tokens": 100, "top_p": 0.9}
        finally:
            _registry._models = original_models

    def test_normalizes_provider_to_lowercase(self) -> None:
        original_models = _registry._models.copy()

        try:
            register_model(
                model_id="func-test-case",
                provider="OPENAI",
                model_name="gpt-4",
            )

            config = _registry.get("func-test-case")
            assert config is not None
            assert config.provider == "openai"
        finally:
            _registry._models = original_models


class TestGetModelConfigFunction:
    """Tests for get_model_config helper function."""

    def test_returns_config_from_global_registry(self) -> None:
        original_models = _registry._models.copy()

        try:
            config = ModelConfig(
                model_id="get-test-model",
                provider="openai",
                model_name="gpt-4",
            )
            _registry.register(config)

            result = get_model_config("get-test-model")

            assert result == config
        finally:
            _registry._models = original_models

    def test_returns_none_for_unknown_model(self) -> None:
        result = get_model_config("nonexistent-model-12345")

        assert result is None


class TestListAvailableModelsFunction:
    """Tests for list_available_models helper function."""

    def test_returns_all_models_from_global_registry(self) -> None:
        original_models = _registry._models.copy()

        try:
            _registry._models.clear()
            config1 = ModelConfig(model_id="list-test-1", provider="openai", model_name="gpt-4")
            config2 = ModelConfig(model_id="list-test-2", provider="ollama", model_name="phi3:mini")
            _registry.register(config1)
            _registry.register(config2)

            result = list_available_models()

            assert len(result) == 2
            assert result["list-test-1"] == config1
            assert result["list-test-2"] == config2
        finally:
            _registry._models = original_models
