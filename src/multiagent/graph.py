"""Langgraph workflow definition for the multiagent system.

This module defines the graph structure and builds the complete workflow.
"""

from langgraph.graph import StateGraph, END

from .state import AgentState
from .nodes import process_jobs_node


def create_workflow() -> StateGraph:
    """
    Create and configure the multiagent workflow graph.

    The workflow consists of:
    1. process_jobs - Receives and prints the job list
    2. END - Terminates the workflow

    Returns:
        Configured StateGraph ready for execution
    """
    # Initialize the graph with our state schema
    workflow = StateGraph(AgentState)

    # Add the processing node
    workflow.add_node("process_jobs", process_jobs_node)

    # Set the entry point
    workflow.set_entry_point("process_jobs")

    # Add edge from process_jobs to END
    workflow.add_edge("process_jobs", END)

    return workflow.compile()
