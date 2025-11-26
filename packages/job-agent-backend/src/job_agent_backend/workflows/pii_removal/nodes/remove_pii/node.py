"""Remove PII node implementation."""

from typing import Dict, Any
from job_agent_backend.model_providers import get_model

from ...state import PIIRemovalState
from .prompts import REMOVE_PII_PROMPT


_pii_model = None


def get_pii_model():
    """
    Get or initialize the PII removal model.

    Uses lazy loading to initialize the model only when needed and cache it
    for subsequent uses.

    Raises:
        Exception: If the model cannot be loaded
    """
    global _pii_model

    if _pii_model is None:
        print("  Loading PII anonymization model...")
        print("  Using phi3:mini via Ollama...")
        try:
            _pii_model = get_model(provider="ollama", model_name="phi3:mini")
            print("  Model loaded successfully!")
        except Exception as e:
            raise RuntimeError(f"Failed to load PII anonymization model (phi3:mini): {e}") from e

    return _pii_model


def anonymize_text(text: str) -> str:
    """
    Anonymize PII in the given text using phi3:mini.

    Args:
        text: Text containing potential PII

    Returns:
        Anonymized text with PII removed

    Raises:
        RuntimeError: If anonymization fails or returns invalid content
    """
    model = get_pii_model()

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


def remove_pii_node(state: Dict[str, Any]) -> PIIRemovalState:
    """
    Anonymize PII from CV content.

    This node uses phi3:mini to detect and remove personally identifiable
    information while preserving professional content.
    This ensures privacy and prevents sensitive data exposure in logs or API calls.

    Args:
        state: Current agent state containing cv_context

    Returns:
        State update containing the anonymized cv_context

    Raises:
        Exception: If the model cannot be loaded or anonymization fails
    """
    cv_context = state.get("cv_context", "")

    job = state.get("job")
    job_id = job.get("job_id") if job else "N/A"

    print("\n" + "=" * 60)
    print(f"Anonymizing PII from CV (job ID: {job_id})...")
    print("=" * 60 + "\n")

    if not cv_context:
        raise ValueError("No CV context available for PII anonymization")

    # Anonymize the CV content - let exceptions propagate
    anonymized_content = anonymize_text(cv_context)

    print(f"  Original CV length: {len(cv_context)} characters")
    print(f"  Anonymized CV length: {len(anonymized_content)} characters\n")

    print("=" * 60)
    print(f"Finished anonymizing PII for job ID {job_id}")
    print("=" * 60 + "\n")

    return {
        "cv_context": anonymized_content,
    }
