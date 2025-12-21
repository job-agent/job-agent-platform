"""AI model abstraction layer for job-agent-backend.

This package provides a flexible system for working with OpenAI, Ollama,
and HuggingFace Transformers models through a unified interface.

Example usage:
    from job_agent_backend.container import get
    from job_agent_backend.model_providers import IModelFactory, IModelRegistry

    # Get the model factory from the DI container
    factory = get(IModelFactory)

    # Create a model on-the-fly by specifying provider and model name
    model = factory.get_model(provider="openai", model_name="gpt-4o-mini")
    result = model.invoke("Hello!")

    # Or use pre-configured models registered in the container
    model = factory.get_model(model_id="skill-extraction")
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
from .registry import ModelRegistry
from .registry_interface import IModelRegistry

__all__ = [
    "ModelFactory",
    "IModelFactory",
    "IModelProvider",
    "IModelRegistry",
    "ModelRegistry",
    "BaseModelProvider",
    "OpenAIProvider",
    "TransformersProvider",
    "OllamaProvider",
]
