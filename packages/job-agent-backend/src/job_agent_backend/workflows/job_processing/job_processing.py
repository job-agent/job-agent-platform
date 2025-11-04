"""Langgraph workflow definition for the workflows system.

This module defines the graph structure and builds the complete workflow.
"""

from typing import Type, Any

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from jobs_repository.repository import JobRepository
from job_agent_backend.workflows.job_processing.nodes import (
    check_job_relevance_node,
    extract_must_have_skills_node,
    extract_nice_to_have_skills_node,
    print_jobs_node,
    create_store_job_node,
)
from job_agent_backend.workflows.job_processing.nodes.check_job_relevance import (
    route_after_relevance_check,
)
from job_agent_backend.workflows.job_processing.state import AgentState


def create_workflow(job_repository_class: Type[Any] = JobRepository) -> CompiledStateGraph:
    """
    Create and configure the workflows workflow graph.

    The workflow processes a single job at a time and consists of:
    1. check_job_relevance - Checks if the job is relevant to the candidate's CV
       - If irrelevant: workflow ends immediately
       - If relevant: continues to next steps
    2. extract_must_have_skills & extract_nice_to_have_skills - Run in parallel
       to extract both types of skills from job description using OpenAI
    3. store_job - Stores relevant jobs to the database (waits for both extraction nodes)
    4. process_jobs - Receives and prints the single job with extracted skills
    5. END - Terminates the workflow

    Note: PII removal should be performed once before running this workflow
    on multiple jobs. See pii_graph.py for the PII removal workflow.

    Args:
        job_repository_class: Job repository class for dependency injection

    Returns:
        Configured StateGraph ready for execution
    """
    # Initialize the graph with our state schema
    workflow = StateGraph(AgentState)

    # Add the job relevance check node
    workflow.add_node("check_job_relevance", check_job_relevance_node)

    # Add the skill extraction nodes (will run in parallel)
    workflow.add_node("extract_must_have_skills", extract_must_have_skills_node)
    workflow.add_node("extract_nice_to_have_skills", extract_nice_to_have_skills_node)

    # Create and add the store job node with injected repository
    store_job_node = create_store_job_node(job_repository_class)
    workflow.add_node("store_job", store_job_node)

    # Add the processing node
    workflow.add_node("process_jobs", print_jobs_node)

    # Set the entry point to job relevance check
    workflow.set_entry_point("check_job_relevance")

    # Add conditional edge after relevance check
    # When job is relevant, both extraction nodes run in parallel
    workflow.add_conditional_edges(
        "check_job_relevance",
        route_after_relevance_check,
        {
            "extract_must_have_skills": "extract_must_have_skills",
            "extract_nice_to_have_skills": "extract_nice_to_have_skills",
            "end": END,
        },
    )

    # Both extraction nodes converge to store_job
    # The framework waits for both to complete before proceeding
    workflow.add_edge("extract_must_have_skills", "store_job")
    workflow.add_edge("extract_nice_to_have_skills", "store_job")

    # Continue the workflow
    workflow.add_edge("store_job", "process_jobs")
    workflow.add_edge("process_jobs", END)

    return workflow.compile(name="JobProcessingWorkflow")
