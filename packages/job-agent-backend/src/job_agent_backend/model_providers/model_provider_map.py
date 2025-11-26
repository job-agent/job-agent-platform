"""Model name to provider mapping.

This mapping allows specifying just model_name without provider.
The provider will be auto-detected based on the model name.
"""

MODEL_PROVIDER_MAP = {
    # OpenAI models
    "gpt-4o-mini": "openai",
    # Ollama models
    "phi3:mini": "ollama",
}
