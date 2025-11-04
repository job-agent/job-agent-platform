"""Remove PII node implementation."""

import os
from typing import Dict, Any

from langchain_openai import ChatOpenAI

from .schemas import ProfessionalInfo
from .prompts import REMOVE_PII_PROMPT
from ...state import PIIRemovalState


def remove_pii_node(state: Dict[str, Any]) -> PIIRemovalState:
    """
    Extract professional information from CV, removing all PII.

    This node uses an LLM to extract only job-relevant professional information
    from the candidate's CV, excluding all personally identifiable information.
    This ensures privacy and prevents sensitive data exposure in logs or API calls.

    Args:
        state: Current agent state containing cv_context

    Returns:
        State update containing the sanitized cv_context when extraction succeeds,
        or an empty dict when no changes are applied
    """
    cv_context = state.get("cv_context", "")

    job = state.get("job")
    job_id = job.get("job_id") if job else "N/A"

    print("\n" + "=" * 60)
    print(f"Extracting professional info from CV (job ID: {job_id})...")
    print("=" * 60 + "\n")

    if not cv_context:
        print("  No CV context available, skipping professional info extraction")
        print("=" * 60 + "\n")
        return {}

    try:
        base_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        structured_llm = base_llm.with_structured_output(ProfessionalInfo)

        messages = REMOVE_PII_PROMPT.invoke({"cv_content": cv_context})

        result: ProfessionalInfo = structured_llm.invoke(messages)

        print(f"  Original CV length: {len(cv_context)} characters")
        print(f"  Professional info length: {len(result.professional_content)} characters\n")

        print("=" * 60)
        print(f"Finished extracting professional info for job ID {job_id}")
        print("=" * 60 + "\n")

        return {
            "cv_context": result.professional_content,
        }

    except Exception as e:
        print(f"  Error extracting professional info - {e}")
        print("  Continuing with original CV content\n")
        print("=" * 60)
        print(f"Failed to extract professional info for job ID {job_id}")
        print("=" * 60 + "\n")

        return {}
