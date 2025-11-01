"""Langgraph workflow for PII removal from CV.

This module defines a separate graph for removing PII from CV content.
This graph should be run once before processing multiple jobs.
"""

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from .nodes import remove_pii_node
from .state import PIIRemovalState


def create_pii_removal_workflow() -> CompiledStateGraph:
    """
    Create and configure the PII removal workflow graph.

    This workflow runs once to remove PII from CV content before
    processing multiple jobs. It consists of:
    1. remove_pii - Removes personally identifiable information from the CV
    2. END - Returns the cleaned CV

    Returns:
        Configured StateGraph ready for execution
    """
    workflow = StateGraph(PIIRemovalState)

    workflow.add_node("remove_pii", remove_pii_node)

    workflow.set_entry_point("remove_pii")

    workflow.add_edge("remove_pii", END)

    return workflow.compile(name="PIIRemovalWorkflow")
