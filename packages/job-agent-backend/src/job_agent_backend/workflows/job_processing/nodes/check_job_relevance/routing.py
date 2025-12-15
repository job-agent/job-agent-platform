"""Routing logic for job relevance check."""

from typing import List
from ...node_names import JobProcessingNode
from ...state import AgentState


def route_after_relevance_check(state: AgentState) -> str | List[str]:
    """
    Route to the next node(s) based on job relevance.

    Args:
        state: Current agent state

    Returns:
        List of node names to execute in parallel if relevant,
        STORE_JOB if irrelevant (to store with is_relevant=False)
    """
    is_relevant = state.get("is_relevant", True)
    if not is_relevant:
        return JobProcessingNode.STORE_JOB
    return [
        JobProcessingNode.EXTRACT_MUST_HAVE_SKILLS,
        JobProcessingNode.EXTRACT_NICE_TO_HAVE_SKILLS,
    ]
