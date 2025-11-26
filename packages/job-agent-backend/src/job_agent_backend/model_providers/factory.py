"""Factory function for creating AI model instances."""

from typing import Any, Optional

from .config import get_model_config
from .providers import OpenAIProvider, TransformersProvider, OllamaProvider


def get_model(
    model_id: Optional[str] = None,
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    **kwargs: Any,
) -> Any:
    """Get an AI model instance based on configuration.

    This factory function provides flexible model creation with three usage patterns:

    1. Use a pre-configured model by ID:
        model = get_model(model_id="skill-extraction")

    2. Override a configured model's parameters:
        model = get_model(model_id="default", temperature=0.5)

    3. Create a custom model on-the-fly:
        model = get_model(provider="openai", model_name="gpt-4")

    Args:
        model_id: ID of a pre-configured model (e.g., "default", "skill-extraction")
        provider: Provider type ("openai", "transformers") - overrides config
        model_name: Model name - overrides config
        temperature: Generation temperature - overrides config
        **kwargs: Additional provider-specific parameters

    Returns:
        An AI model instance (e.g., LangChain chat model, embedding model, etc.)

    Raises:
        ValueError: If neither model_id nor (provider + model_name) are provided
        ValueError: If model_id is not found in configuration
        ValueError: If provider type is not supported

    Examples:
        # Use pre-configured model
        model = get_model(model_id="default")

        # Override temperature for a configured model
        model = get_model(model_id="skill-extraction", temperature=0.7)

        # Create custom model
        model = get_model(provider="openai", model_name="gpt-4")

        # Use with structured output (for chat models)
        structured_model = get_model(model_id="default").with_structured_output(MySchema)
    """
    config = None

    # Load configuration if model_id is provided
    if model_id:
        config = get_model_config(model_id)
        if not config:
            raise ValueError(
                f"Model '{model_id}' not found in configuration. "
                f"Available models: {list(get_model_config.__globals__['_registry'].list_models().keys())}"
            )

    # If no config and no provider/model_name, error
    if not config and not (provider and model_name):
        raise ValueError("Either 'model_id' or both 'provider' and 'model_name' must be provided")

    # Determine final parameters (command-line args override config)
    final_provider = provider or (config.provider if config else None)
    final_model_name = model_name or (config.model_name if config else None)
    final_temperature = (
        temperature if temperature is not None else (config.temperature if config else 0.0)
    )

    # Merge kwargs from config and function call
    final_kwargs = {}
    if config:
        final_kwargs.update(config.kwargs)
    final_kwargs.update(kwargs)

    # Create provider instance based on type
    provider_map = {
        "openai": OpenAIProvider,
        "transformers": TransformersProvider,
        "ollama": OllamaProvider,
    }

    provider_class = provider_map.get(final_provider.lower())
    if not provider_class:
        raise ValueError(
            f"Unsupported provider: {final_provider}. "
            f"Supported providers: {list(provider_map.keys())}"
        )

    # Instantiate provider and get model
    provider_instance = provider_class(
        model_name=final_model_name, temperature=final_temperature, **final_kwargs
    )

    return provider_instance.get_model()
