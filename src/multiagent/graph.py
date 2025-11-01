"""Langgraph workflow definition for the multiagent system.

This module defines the graph structure and builds the complete workflow.
"""

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from .state import AgentState
from .nodes import print_jobs_node, extract_must_have_skills_node, check_job_relevance_node, remove_pii_node


def create_workflow() -> CompiledStateGraph:
    """
    Create and configure the multiagent workflow graph.

    The workflow processes a single job at a time and consists of:
    1. remove_pii - Removes personally identifiable information from the CV
    2. check_job_relevance - Checks if the job is relevant to the candidate's CV
    3. extract_skills - Extracts must-have skills from a job description using OpenAI
    4. process_jobs - Receives and prints the single job with extracted skills
    5. END - Terminates the workflow

    Returns:
        Configured StateGraph ready for execution
    """
    # Initialize the graph with our state schema
    workflow = StateGraph(AgentState)

    # Add the PII removal node
    workflow.add_node("remove_pii", remove_pii_node)

    # Add the job relevance check node
    workflow.add_node("check_job_relevance", check_job_relevance_node)

    # Add the skill extraction node
    workflow.add_node("extract_skills", extract_must_have_skills_node)

    # Add the processing node
    workflow.add_node("process_jobs", print_jobs_node)

    # Set the entry point to PII removal
    workflow.set_entry_point("remove_pii")

    # Add edges: remove_pii -> check_job_relevance -> extract_skills -> process_jobs -> END
    workflow.add_edge("remove_pii", "check_job_relevance")
    workflow.add_edge("check_job_relevance", "extract_skills")
    workflow.add_edge("extract_skills", "process_jobs")
    workflow.add_edge("process_jobs", END)

    return workflow.compile()
