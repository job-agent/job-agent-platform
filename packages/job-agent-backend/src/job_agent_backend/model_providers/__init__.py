"""AI model abstraction layer for job-agent-backend.

This package provides a flexible system for working with OpenAI and HuggingFace Transformers models
through a unified interface.

Supports various model types: chat models, embeddings, and more.

Quick Start:
    1. Configure models via environment variables:
        export MODEL_default_PROVIDER=openai
        export MODEL_default_MODEL_NAME=gpt-4o-mini

    2. Use in your code:
        from job_agent_backend.model_providers import get_model

        model = get_model(model_id="default")
        result = model.invoke("Hello!")

For more details, see the documentation in config.py and factory.py.
"""

from .config import (
    ModelConfig,
    register_model,
    get_model_config,
    list_available_models,
)
from .factory import get_model, ModelFactory
from .interfaces import IModelFactory
from .providers import (
    BaseModelProvider,
    OpenAIProvider,
    TransformersProvider,
    OllamaProvider,
)

__all__ = [
    # Factory function (main entry point)
    "get_model",
    # Factory class and interface for DI
    "ModelFactory",
    "IModelFactory",
    # Configuration
    "ModelConfig",
    "register_model",
    "get_model_config",
    "list_available_models",
    # Provider classes (for advanced usage)
    "BaseModelProvider",
    "OpenAIProvider",
    "TransformersProvider",
    "OllamaProvider",
]
