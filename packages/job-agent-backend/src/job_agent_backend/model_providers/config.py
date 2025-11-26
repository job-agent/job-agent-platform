"""Configuration system for AI models.

This module provides a flexible configuration system that allows you to:
1. Define multiple models with unique IDs
2. Configure models via environment variables or code

Example configuration via environment variables:
    # Define model configurations
    export MODEL_default_PROVIDER=openai
    export MODEL_default_MODEL_NAME=gpt-4o-mini
    export MODEL_default_TEMPERATURE=0.0

    export MODEL_skill_extraction_PROVIDER=openai
    export MODEL_skill_extraction_MODEL_NAME=gpt-4
    export MODEL_skill_extraction_TEMPERATURE=0.0

    export MODEL_pii_anonymizer_PROVIDER=transformers
    export MODEL_pii_anonymizer_MODEL_NAME=ai4privacy/llama-ai4privacy-english-anonymiser-openpii
    export MODEL_pii_anonymizer_TEMPERATURE=0.0

Example usage:
    from job_agent_backend.model_providers import get_model

    # Use configured model
    model = get_model(model_id="skill-extraction")

    # Or override with custom config
    model = get_model(
        model_id="custom",
        provider="openai",
        model_name="gpt-4"
    )
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ModelConfig:
    """Configuration for a single AI model.

    Attributes:
        model_id: Unique identifier for this model configuration
        provider: Provider type ('openai', 'transformers')
        model_name: Provider-specific model name
        temperature: Generation temperature (0.0 = deterministic, for chat models)
        kwargs: Additional provider-specific parameters
    """
    model_id: str
    provider: str
    model_name: str
    temperature: float = 0.0
    kwargs: Dict[str, Any] = field(default_factory=dict)


class ModelRegistry:
    """Registry for managing model configurations.

    This class handles loading model configurations from environment variables
    and provides a central registry for accessing them.
    """

    def __init__(self):
        self._models: Dict[str, ModelConfig] = {}
        self._load_from_env()

    def _load_from_env(self):
        """Load model configurations from environment variables.

        Expected format:
            MODEL_{model_id}_{PARAMETER}=value

        Example:
            MODEL_default_PROVIDER=openai
            MODEL_default_MODEL_NAME=gpt-4o-mini
            MODEL_default_TEMPERATURE=0.0
        """
        # Scan environment variables for model configurations
        prefix = "MODEL_"
        model_ids = set()

        for key in os.environ:
            if key.startswith(prefix):
                # Extract model_id from key (e.g., MODEL_default_PROVIDER -> default)
                parts = key[len(prefix):].split("_")
                if len(parts) >= 2:
                    # Join all parts except the last one to handle model_ids with underscores
                    # e.g., MODEL_skill_extraction_PROVIDER -> skill_extraction
                    model_id = "_".join(parts[:-1])
                    model_ids.add(model_id)

        # Load each model configuration
        for model_id in model_ids:
            self._load_model_config(model_id)

    def _load_model_config(self, model_id: str):
        """Load configuration for a specific model from environment.

        Args:
            model_id: The model identifier to load
        """
        prefix = f"MODEL_{model_id}_"

        provider = os.getenv(f"{prefix}PROVIDER")
        model_name = os.getenv(f"{prefix}MODEL_NAME")

        if not provider or not model_name:
            return  # Skip incomplete configurations

        temperature_str = os.getenv(f"{prefix}TEMPERATURE", "0.0")
        try:
            temperature = float(temperature_str)
        except ValueError:
            temperature = 0.0

        # Collect additional kwargs
        kwargs = {}
        for key, value in os.environ.items():
            if key.startswith(prefix):
                param = key[len(prefix):]
                if param not in ("PROVIDER", "MODEL_NAME", "TEMPERATURE"):
                    # Convert to lowercase for kwargs
                    kwargs[param.lower()] = value

        config = ModelConfig(
            model_id=model_id,
            provider=provider.lower(),
            model_name=model_name,
            temperature=temperature,
            kwargs=kwargs
        )

        self.register(config)

    def register(self, config: ModelConfig):
        """Register a model configuration.

        Args:
            config: ModelConfig instance to register
        """
        self._models[config.model_id] = config

    def get(self, model_id: str) -> Optional[ModelConfig]:
        """Get a model configuration by ID.

        Args:
            model_id: The model identifier

        Returns:
            ModelConfig if found, None otherwise
        """
        return self._models.get(model_id)

    def list_models(self) -> Dict[str, ModelConfig]:
        """Get all registered model configurations.

        Returns:
            Dictionary mapping model IDs to their configurations
        """
        return self._models.copy()


# Global registry instance
_registry = ModelRegistry()


def register_model(
    model_id: str,
    provider: str,
    model_name: str,
    temperature: float = 0.0,
    **kwargs: Any
):
    """Register a new model configuration programmatically.

    Args:
        model_id: Unique identifier for this model
        provider: Provider type ('openai', 'transformers')
        model_name: Provider-specific model name
        temperature: Generation temperature
        **kwargs: Additional provider-specific parameters

    Example:
        register_model(
            model_id="my-model",
            provider="transformers",
            model_name="ai4privacy/llama-ai4privacy-english-anonymiser-openpii",
            temperature=0.0
        )
    """
    config = ModelConfig(
        model_id=model_id,
        provider=provider.lower(),
        model_name=model_name,
        temperature=temperature,
        kwargs=kwargs
    )
    _registry.register(config)


def get_model_config(model_id: str) -> Optional[ModelConfig]:
    """Get a model configuration by ID.

    Args:
        model_id: The model identifier

    Returns:
        ModelConfig if found, None otherwise
    """
    return _registry.get(model_id)


def list_available_models() -> Dict[str, ModelConfig]:
    """List all available model configurations.

    Returns:
        Dictionary mapping model IDs to their configurations
    """
    return _registry.list_models()
