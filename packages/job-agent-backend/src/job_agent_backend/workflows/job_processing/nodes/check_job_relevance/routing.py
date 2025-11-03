"""Routing logic for job relevance check."""

from typing import List
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
    # Return both extraction nodes to run in parallel
    return ["extract_must_have_skills", "extract_nice_to_have_skills"]
