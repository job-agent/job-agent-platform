"""Provider string to provider class mapping.

This mapping allows looking up provider classes by their string identifiers.
"""

from ..providers import OpenAIProvider, OllamaProvider, TransformersProvider

PROVIDER_MAP = {
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
    "transformers": TransformersProvider,
}
