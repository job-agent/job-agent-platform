"""Main PII removal system interface.

This module provides the public API for running the PII removal workflow.
"""

import os

from .pii_removal import create_pii_removal_workflow
from .state import PIIRemovalState


def run_pii_removal(cv_content: str) -> str:
    """
    Remove personally identifiable information from CV content.

    This is the main entry point for the PII removal workflow. It accepts
    CV content and returns a cleaned version with PII removed.

    Args:
        cv_content: The raw CV content to clean

    Returns:
        The CV content with PII removed

    Raises:
        ValueError: If cv_content is empty or None

    Example:
        >>> cv_content = "My name is John Doe, email: john@example.com..."
        >>> cleaned_cv = run_pii_removal(cv_content)
        >>> print(cleaned_cv)
        "My name is [REDACTED], email: [REDACTED]..."
    """

    tracing_enabled = os.getenv("LANGSMITH_TRACING_V2", "").lower() == "true"
    project_name = os.getenv("LANGSMITH_PROJECT", "default")

    if tracing_enabled:
        print(f"🔍 LangSmith tracing enabled - Project: {project_name}")
        print("   View traces at: https://smith.langchain.com/\n")

    if not cv_content:
        raise ValueError("CV content is required but was not provided")

    workflow = create_pii_removal_workflow()

    initial_state: PIIRemovalState = {"cv_context": cv_content}

    final_state = workflow.invoke(initial_state)

    print("PII removal completed successfully")

    return final_state["cv_context"]
