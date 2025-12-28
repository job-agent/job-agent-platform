"""AI model abstraction layer for job-agent-backend.

This package provides a flexible system for working with OpenAI, Ollama,
and HuggingFace Transformers models through a unified interface.

Example usage:
    from job_agent_backend.container import get_model_factory_instance

    # Get the model factory from the DI container
    factory = get_model_factory_instance()

    # Create a model on-the-fly by specifying provider and model name
    model = factory.get_model(provider="openai", model_name="gpt-4o-mini")
    result = model.invoke("Hello!")

    # Or use pre-configured models registered in the container
    model = factory.get_model(model_id="skill-extraction")
"""

from .factory import ModelFactory
from ..contracts.model_factory_interface import IModelFactory
from .providers import (
    BaseModelProvider,
    OpenAIProvider,
    TransformersProvider,
    OllamaProvider,
)
from .contracts.provider_interface import IModelProvider
from .registry import ModelRegistry
from .contracts.registry_interface import IModelRegistry

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
