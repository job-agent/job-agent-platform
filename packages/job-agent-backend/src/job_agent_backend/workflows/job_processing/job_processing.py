"""Langgraph workflow definition for the workflows system.

This module defines the graph structure and builds the complete workflow.
"""

from collections.abc import Mapping
from typing import Callable, Tuple, TypeGuard

from job_agent_platform_contracts import IJobRepository
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from langchain_core.runnables import RunnableConfig

from job_agent_backend.contracts import IModelFactory
from job_agent_backend.workflows.job_processing.node_names import JobProcessingNode
from job_agent_backend.workflows.job_processing.nodes import (
    create_check_job_relevance_node,
    create_extract_must_have_skills_node,
    create_extract_nice_to_have_skills_node,
    print_jobs_node,
    create_store_job_node,
)
from job_agent_backend.workflows.job_processing.nodes.check_job_relevance import (
    route_after_relevance_check,
)
from job_agent_backend.workflows.job_processing.state import AgentState, as_node


def _is_job_repository_factory(val: object) -> TypeGuard[Callable[[], IJobRepository]]:
    """Check if value is a valid job repository factory callable."""
    return callable(val)


def _is_model_factory(val: object) -> TypeGuard[IModelFactory]:
    """Check if value is a valid model factory."""
    return val is not None


def create_workflow(config: RunnableConfig) -> CompiledStateGraph:
    """
    Create and configure the workflows workflow graph.

    The workflow processes a single job at a time and consists of:
    1. check_job_relevance - Checks if the job is relevant to the candidate's CV
       - If relevant: continues to skill extraction
       - If irrelevant: skips to store_job (stored with is_relevant=False)
    2. extract_must_have_skills & extract_nice_to_have_skills - Run in parallel
       to extract both types of skills from job description using OpenAI
       (only for relevant jobs)
    3. store_job - Stores all jobs to the database with is_relevant flag
       - Relevant jobs: stored with extracted skills and is_relevant=True
       - Irrelevant jobs: stored without skills and is_relevant=False
    4. process_jobs - Receives and prints the single job with extracted skills
    5. END - Terminates the workflow

    Note: PII removal should be performed once before running this workflow
    on multiple jobs. See pii_graph.py for the PII removal workflow.

    Args:
        config: Runnable configuration providing dependency overrides

    Returns:
        Configured StateGraph ready for execution
    """
    job_repository_factory, model_factory = _resolve_dependencies(config)

    workflow = StateGraph(AgentState)

    check_job_relevance_node = create_check_job_relevance_node(model_factory)
    workflow.add_node(JobProcessingNode.CHECK_JOB_RELEVANCE, as_node(check_job_relevance_node))

    extract_must_have_skills_node = create_extract_must_have_skills_node(model_factory)
    workflow.add_node(
        JobProcessingNode.EXTRACT_MUST_HAVE_SKILLS, as_node(extract_must_have_skills_node)
    )

    extract_nice_to_have_skills_node = create_extract_nice_to_have_skills_node(model_factory)
    workflow.add_node(
        JobProcessingNode.EXTRACT_NICE_TO_HAVE_SKILLS,
        as_node(extract_nice_to_have_skills_node),
    )

    store_job_node = create_store_job_node(job_repository_factory)
    workflow.add_node(JobProcessingNode.STORE_JOB, as_node(store_job_node))

    workflow.add_node(JobProcessingNode.PROCESS_JOBS, as_node(print_jobs_node))

    workflow.set_entry_point(JobProcessingNode.CHECK_JOB_RELEVANCE)

    workflow.add_conditional_edges(
        JobProcessingNode.CHECK_JOB_RELEVANCE,
        route_after_relevance_check,
        {
            JobProcessingNode.EXTRACT_MUST_HAVE_SKILLS: JobProcessingNode.EXTRACT_MUST_HAVE_SKILLS,
            JobProcessingNode.EXTRACT_NICE_TO_HAVE_SKILLS: JobProcessingNode.EXTRACT_NICE_TO_HAVE_SKILLS,
            JobProcessingNode.STORE_JOB: JobProcessingNode.STORE_JOB,
        },
    )

    workflow.add_edge(
        JobProcessingNode.EXTRACT_MUST_HAVE_SKILLS,
        JobProcessingNode.STORE_JOB,
    )
    workflow.add_edge(
        JobProcessingNode.EXTRACT_NICE_TO_HAVE_SKILLS,
        JobProcessingNode.STORE_JOB,
    )

    workflow.add_edge(JobProcessingNode.STORE_JOB, JobProcessingNode.PROCESS_JOBS)
    workflow.add_edge(JobProcessingNode.PROCESS_JOBS, END)

    return workflow.compile(name="JobProcessingWorkflow")


def _resolve_dependencies(
    config: RunnableConfig,
) -> Tuple[Callable[[], IJobRepository], IModelFactory]:
    """
    Resolve required dependencies from the RunnableConfig.

    Args:
        config: Runnable configuration containing dependency overrides

    Returns:
        Tuple of (job_repository_factory, model_factory)

    Raises:
        ValueError: If required dependencies are not configured
    """
    if isinstance(config, Mapping):
        config_values: Mapping[str, object] = config
        configurable = config.get("configurable")
        if isinstance(configurable, Mapping):
            config_values = configurable

        job_repository_factory = config_values.get("job_repository_factory")
        model_factory = config_values.get("model_factory")

        if not _is_job_repository_factory(job_repository_factory):
            raise ValueError("job_repository_factory dependency is not configured")

        if not _is_model_factory(model_factory):
            raise ValueError("model_factory dependency is not configured")

        return (job_repository_factory, model_factory)

    raise ValueError("Configuration is not a valid Mapping")
