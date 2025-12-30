"""Check job relevance node implementation."""

import logging
from typing import Callable

from job_agent_backend.contracts import IModelFactory
from job_agent_backend.utils import cosine_similarity
from ...state import AgentState
from .result import CheckRelevanceResult

logger = logging.getLogger(__name__)


def create_check_job_relevance_node(
    model_factory: IModelFactory,
) -> Callable[[AgentState], CheckRelevanceResult]:
    """
    Factory function to create a check_job_relevance_node with injected dependencies.

    Args:
        model_factory: Factory used to create model instances

    Returns:
        Configured check_job_relevance_node function
    """

    def check_job_relevance_node(state: AgentState) -> CheckRelevanceResult:
        """
        Check if a job is relevant to the candidate based on their CV.

        This node uses an LLM to determine job relevance by comparing the job
        posting against the candidate's CV. It's configured to be lenient and
        default to marking jobs as relevant unless they're clearly mismatched.

        Args:
            state: Current agent state containing job and cv_context

        Returns:
            State update containing the "is_relevant" flag based on the LLM decision
        """
        job = state["job"]
        job_id = job.get("job_id")
        cv_context = state.get("cv_context", "")

        logger.info("Checking relevance for job ID %s", job_id)

        if not cv_context:
            logger.info("Job (ID: %s): No CV context available, assuming relevant", job_id)
            return {"is_relevant": True}

        job_title = job.get("title", "Unknown")
        job_description = job.get("description", "")

        if not job_description:
            logger.info("Job (ID: %s): No description available, assuming relevant", job_id)
            return {"is_relevant": True}

        try:
            model = model_factory.get_model(model_id="embedding")

            # Prepare texts for embedding
            # We combine title and description for the job representation
            job_text = f"{job_title}\n\n{job_description}"

            # Embed both texts
            cv_embedding = model.embed_query(cv_context)
            job_embedding = model.embed_query(job_text)

            # Calculate cosine similarity
            similarity = cosine_similarity(cv_embedding, job_embedding)

            # Threshold for relevance
            # 0.4 is a reasonable starting point for multilingual-cased-v2
            # It allows for some semantic overlap without requiring exact matches
            THRESHOLD = 0.4

            is_relevant = bool(similarity >= THRESHOLD)
            relevance_status = "RELEVANT" if is_relevant else "IRRELEVANT"

            logger.info("Job (ID: %s): %s (Similarity: %.4f)", job_id, relevance_status, similarity)

        except Exception as e:
            logger.warning(
                "Job (ID: %s): Error checking relevance - %s. Assuming relevant by default",
                job_id,
                e,
            )
            is_relevant = True

        logger.info("Finished checking relevance for job ID %s", job_id)

        return {"is_relevant": is_relevant}

    return check_job_relevance_node
