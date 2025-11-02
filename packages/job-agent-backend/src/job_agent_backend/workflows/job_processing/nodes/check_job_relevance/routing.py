"""Routing logic for job relevance check."""

from ...state import AgentState


def route_after_relevance_check(state: AgentState) -> str:
    """
    Route to the next node based on job relevance.

    Args:
        state: Current agent state

    Returns:
        Next node name: "extract_skills" if relevant, "end" if irrelevant
    """
    is_relevant = state.get("is_relevant", True)  # Default to True if not set
    if not is_relevant:
        return "end"
    return "extract_skills"
