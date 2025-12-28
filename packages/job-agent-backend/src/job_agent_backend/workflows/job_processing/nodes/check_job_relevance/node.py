"""Check job relevance node implementation."""

from typing import Callable

from .....model_providers import IModelFactory
from ...state import AgentState
from .result import CheckRelevanceResult


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

        print("\n" + "=" * 60)
        print(f"Checking relevance for job ID {job_id}...")
        print("=" * 60 + "\n")

        if not cv_context:
            print(f"  Job (ID: {job_id}): No CV context available, assuming relevant")
            print("=" * 60 + "\n")
            return {"is_relevant": True}

        job_title = job.get("title", "Unknown")
        job_description = job.get("description", "")

        if not job_description:
            print(f"  Job (ID: {job_id}): No description available, assuming relevant")
            print("=" * 60 + "\n")
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
            import numpy as np

            def cosine_similarity(a, b):
                return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

            similarity = cosine_similarity(cv_embedding, job_embedding)

            # Threshold for relevance
            # 0.4 is a reasonable starting point for multilingual-cased-v2
            # It allows for some semantic overlap without requiring exact matches
            THRESHOLD = 0.4

            is_relevant = bool(similarity >= THRESHOLD)
            relevance_status = "RELEVANT" if is_relevant else "IRRELEVANT"

            print(f"  Job (ID: {job_id}): {relevance_status} (Similarity: {similarity:.4f})")

        except Exception as e:
            print(f"  Job (ID: {job_id}): Error checking relevance - {e}")
            print("    Assuming relevant by default\n")
            is_relevant = True

        print("=" * 60)
        print(f"Finished checking relevance for job ID {job_id}")
        print("=" * 60 + "\n")

        return {"is_relevant": is_relevant}

    return check_job_relevance_node
