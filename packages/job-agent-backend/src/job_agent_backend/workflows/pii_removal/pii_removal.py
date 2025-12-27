"""Langgraph workflow for PII removal from CV.

This module defines a separate graph for removing PII from CV content.
This graph should be run once before processing multiple jobs.
"""

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from job_agent_backend.model_providers import IModelFactory
from .node_names import PIIRemovalNode
from .nodes import create_remove_pii_node
from .state import PIIRemovalState


def create_pii_removal_workflow(model_factory: IModelFactory) -> CompiledStateGraph:
    """
    Create and configure the PII removal workflow graph.

    This workflow runs once to remove PII from CV content before
    processing multiple jobs. It consists of:
    1. remove_pii - Removes personally identifiable information from the CV
    2. END - Returns the cleaned CV

    Args:
        model_factory: Factory for creating AI model instances

    Returns:
        Configured StateGraph ready for execution
    """
    workflow = StateGraph(PIIRemovalState)

    remove_pii_node = create_remove_pii_node(model_factory)
    workflow.add_node(PIIRemovalNode.REMOVE_PII, remove_pii_node)

    workflow.set_entry_point(PIIRemovalNode.REMOVE_PII)

    workflow.add_edge(PIIRemovalNode.REMOVE_PII, END)

    return workflow.compile(name="PIIRemovalWorkflow")
