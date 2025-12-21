"""AI model abstraction layer for job-agent-backend.

This package provides a flexible system for working with OpenAI, Ollama,
and HuggingFace Transformers models through a unified interface.

Example usage:
    from job_agent_backend.container import get
    from job_agent_backend.model_providers import IModelFactory

    factory = get(IModelFactory)
    model = factory.get_model(provider="openai", model_name="gpt-4o-mini")
    result = model.invoke("Hello!")
"""

from .factory import ModelFactory
from .factory_interface import IModelFactory
from .providers import (
    IModelProvider,
    BaseModelProvider,
    OpenAIProvider,
    TransformersProvider,
    OllamaProvider,
)

__all__ = [
    "ModelFactory",
    "IModelFactory",
    "IModelProvider",
    "BaseModelProvider",
    "OpenAIProvider",
    "TransformersProvider",
    "OllamaProvider",
]
