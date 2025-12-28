"""Remove PII node implementation."""

import logging
from typing import Callable, Dict, Any

from job_agent_backend.contracts import IModelFactory
from .helpers import create_anonymize_text
from .result import RemovePIIResult

logger = logging.getLogger(__name__)


def create_remove_pii_node(
    model_factory: IModelFactory,
) -> Callable[[Dict[str, Any]], RemovePIIResult]:
    """
    Factory function to create a remove_pii_node with injected dependencies.

    Args:
        model_factory: Factory used to create model instances

    Returns:
        Configured remove_pii_node function
    """
    anonymize_text = create_anonymize_text(model_factory)

    def remove_pii_node(state: Dict[str, Any]) -> RemovePIIResult:
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

        logger.info("Anonymizing PII from CV (job ID: %s)", job_id)

        if not cv_context:
            raise ValueError("No CV context available for PII anonymization")

        # Anonymize the CV content - let exceptions propagate
        anonymized_content = anonymize_text(cv_context)

        logger.info(
            "Original CV length: %d characters, Anonymized CV length: %d characters",
            len(cv_context),
            len(anonymized_content),
        )

        logger.info("Finished anonymizing PII for job ID %s", job_id)

        return {
            "cv_context": anonymized_content,
        }

    return remove_pii_node
