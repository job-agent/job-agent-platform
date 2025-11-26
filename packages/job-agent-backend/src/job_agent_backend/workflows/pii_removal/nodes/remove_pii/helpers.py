"""Helper functions for PII removal."""

from job_agent_backend.model_providers import get_model

from .prompts import REMOVE_PII_PROMPT


def anonymize_text(text: str) -> str:
    """
    Anonymize PII in the given text using phi3:mini via Ollama.

    Args:
        text: Text containing potential PII

    Returns:
        Anonymized text with PII removed

    Raises:
        RuntimeError: If anonymization fails or returns invalid content
    """
    # Get model (provider auto-detected, cached by factory)
    model = get_model(model_name="phi3:mini")

    messages = REMOVE_PII_PROMPT.format_messages(cv_content=text)

    try:
        response = model.invoke(messages)
    except Exception as e:
        raise RuntimeError(f"Failed to invoke PII anonymization model: {e}") from e

    if hasattr(response, "content"):
        anonymized_text = response.content
    else:
        anonymized_text = str(response)

    anonymized_text = anonymized_text.strip()

    if not anonymized_text:
        raise RuntimeError("PII anonymization returned empty content")

    return anonymized_text
