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
        List of node names to execute in parallel if relevant, "end" if irrelevant
    """
    is_relevant = state.get("is_relevant", True)  # Default to True if not set
    if not is_relevant:
        return "end"
    return [
        JobProcessingNode.EXTRACT_MUST_HAVE_SKILLS,
        JobProcessingNode.EXTRACT_NICE_TO_HAVE_SKILLS,
    ]
