"""Langgraph workflow definition for the workflows system.

This module defines the graph structure and builds the complete workflow.
"""

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from job_agent_backend.workflows.job_processing.nodes import (
    check_job_relevance_node,
    extract_must_have_skills_node,
    print_jobs_node,
    store_job_node,
)
from job_agent_backend.workflows.job_processing.nodes.check_job_relevance import (
    route_after_relevance_check,
)
from job_agent_backend.workflows.job_processing.state import AgentState


def create_workflow() -> CompiledStateGraph:
    """
    Create and configure the workflows workflow graph.

    The workflow processes a single job at a time and consists of:
    1. check_job_relevance - Checks if the job is relevant to the candidate's CV
       - If irrelevant: workflow ends immediately
       - If relevant: continues to next steps
    2. extract_skills - Extracts must-have skills from a job description using OpenAI
    3. store_job - Stores relevant jobs to the database
    4. process_jobs - Receives and prints the single job with extracted skills
    5. END - Terminates the workflow

    Note: PII removal should be performed once before running this workflow
    on multiple jobs. See pii_graph.py for the PII removal workflow.

    Returns:
        Configured StateGraph ready for execution
    """
    # Initialize the graph with our state schema
    workflow = StateGraph(AgentState)

    # Add the job relevance check node
    workflow.add_node("check_job_relevance", check_job_relevance_node)

    # Add the skill extraction node
    workflow.add_node("extract_skills", extract_must_have_skills_node)

    # Add the store job node
    workflow.add_node("store_job", store_job_node)

    # Add the processing node
    workflow.add_node("process_jobs", print_jobs_node)

    # Set the entry point to job relevance check
    workflow.set_entry_point("check_job_relevance")

    # Add conditional edge after relevance check
    workflow.add_conditional_edges(
        "check_job_relevance",
        route_after_relevance_check,
        {
            "extract_skills": "extract_skills",
            "end": END,
        },
    )

    # Add remaining edges for relevant jobs
    workflow.add_edge("extract_skills", "store_job")
    workflow.add_edge("store_job", "process_jobs")
    workflow.add_edge("process_jobs", END)

    return workflow.compile(name="JobProcessingWorkflow")
