"""Remove PII node implementation."""

from typing import Dict, Any
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

from ...state import PIIRemovalState


# Global variables to cache the model and pipeline
_pii_model = None
_pii_tokenizer = None
_pii_pipeline = None


def get_pii_pipeline():
    """
    Get or initialize the PII removal pipeline.

    Uses lazy loading to initialize the model only when needed and cache it
    for subsequent uses.
    """
    global _pii_model, _pii_tokenizer, _pii_pipeline

    if _pii_pipeline is None:
        print("  Loading ai4privacy PII anonymization model (first time only)...")
        model_name = "ai4privacy/llama-ai4privacy-english-anonymiser-openpii"

        _pii_tokenizer = AutoTokenizer.from_pretrained(model_name)
        _pii_model = AutoModelForTokenClassification.from_pretrained(model_name)
        _pii_pipeline = pipeline(
            "token-classification",
            model=_pii_model,
            tokenizer=_pii_tokenizer,
            aggregation_strategy="simple"
        )
        print("  Model loaded successfully!")

    return _pii_pipeline


def anonymize_text(text: str) -> str:
    """
    Anonymize PII in the given text using the ai4privacy model.

    Args:
        text: Text containing potential PII

    Returns:
        Anonymized text with PII entities replaced by placeholders
    """
    pii_pipeline = get_pii_pipeline()

    # Process the text with the pipeline
    results = pii_pipeline(text)

    # Sort results by start position in reverse order to avoid offset issues
    results = sorted(results, key=lambda x: x['start'], reverse=True)

    # Replace PII entities with placeholders
    anonymized_text = text
    for entity in results:
        start = entity['start']
        end = entity['end']
        entity_type = entity['entity_group']

        # Create a placeholder based on entity type
        placeholder = f"[{entity_type.upper()}]"

        # Replace the entity with the placeholder
        anonymized_text = anonymized_text[:start] + placeholder + anonymized_text[end:]

    return anonymized_text


def remove_pii_node(state: Dict[str, Any]) -> PIIRemovalState:
    """
    Anonymize PII from CV content.

    This node uses the ai4privacy/llama-ai4privacy-english-anonymiser-openpii model
    to detect and replace personally identifiable information with placeholders.
    This ensures privacy and prevents sensitive data exposure in logs or API calls.

    Args:
        state: Current agent state containing cv_context

    Returns:
        State update containing the anonymized cv_context when anonymization succeeds,
        or an empty dict when no changes are applied
    """
    cv_context = state.get("cv_context", "")

    job = state.get("job")
    job_id = job.get("job_id") if job else "N/A"

    print("\n" + "=" * 60)
    print(f"Anonymizing PII from CV (job ID: {job_id})...")
    print("=" * 60 + "\n")

    if not cv_context:
        print("  No CV context available, skipping PII anonymization")
        print("=" * 60 + "\n")
        return {}

    try:
        # Anonymize the CV content
        anonymized_content = anonymize_text(cv_context)

        print(f"  Original CV length: {len(cv_context)} characters")
        print(f"  Anonymized CV length: {len(anonymized_content)} characters\n")

        print("=" * 60)
        print(f"Finished anonymizing PII for job ID {job_id}")
        print("=" * 60 + "\n")

        return {
            "cv_context": anonymized_content,
        }

    except Exception as e:
        print(f"  Error anonymizing PII - {e}")
        print("  Continuing with original CV content\n")
        print("=" * 60)
        print(f"Failed to anonymize PII for job ID {job_id}")
        print("=" * 60 + "\n")

        return {}
