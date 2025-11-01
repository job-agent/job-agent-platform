"""Langgraph workflow definition for the multiagent system.

This module defines the graph structure and builds the complete workflow.
"""

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from .state import AgentState
from .nodes import print_jobs_node, extract_skills_node


def create_workflow() -> CompiledStateGraph:
    """
    Create and configure the multiagent workflow graph.

    The workflow consists of:
    1. extract_skills - Extracts must-have skills from job descriptions using OpenAI
    2. process_jobs - Receives and prints the job list with extracted skills
    3. END - Terminates the workflow

    Returns:
        Configured StateGraph ready for execution
    """
    # Initialize the graph with our state schema
    workflow = StateGraph(AgentState)

    # Add the skill extraction node
    workflow.add_node("extract_skills", extract_skills_node)

    # Add the processing node
    workflow.add_node("process_jobs", print_jobs_node)

    # Set the entry point to skill extraction
    workflow.set_entry_point("extract_skills")

    # Add edges: extract_skills -> process_jobs -> END
    workflow.add_edge("extract_skills", "process_jobs")
    workflow.add_edge("process_jobs", END)

    return workflow.compile()
