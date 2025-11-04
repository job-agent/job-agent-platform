"""Main workflows system interface.

This module provides the public API for running the workflows system.
"""

import os
from typing import Callable

from job_agent_platform_contracts import IJobRepository

from job_scrapper_contracts import JobDict

from .job_processing import create_workflow
from .state import AgentState


def run_job_processing(
    job: JobDict,
    cv_content: str,
    job_repository_factory: Callable[[], IJobRepository],
) -> AgentState:
    """
    Run the workflows system on a single job.

    This is the main entry point for the workflows system. It accepts a single
    job dictionary and processes it through the langgraph workflow.

    Args:
        job: A single job dictionary to process
        cv_content: The CV content to match against the job
        job_repository_factory: Factory for producing job repository instances

    Returns:
        Final agent state containing job processing results including:
        - is_relevant: Whether the job is relevant to the candidate
        - extracted_must_have_skills: List of must-have skills (for relevant jobs)
        - extracted_nice_to_have_skills: List of nice-to-have skills (for relevant jobs)
        - status: Final workflow status

    Raises:
        ValueError: If cv_content is empty or None

    Example:
        >>> job = {"title": "Python Developer", "salary": 5000}
        >>> cv_content = "My CV content..."
        >>> result = run_job_processing(job, cv_content)
        >>> if result.get("is_relevant"):
        >>>     print(f"Relevant job with skills: {result.get('extracted_must_have_skills')}")
    """

    tracing_enabled = os.getenv("LANGSMITH_TRACING_V2", "").lower() == "true"
    project_name = os.getenv("LANGSMITH_PROJECT", "default")

    if tracing_enabled:
        print(f"🔍 LangSmith tracing enabled - Project: {project_name}")
        print("   View traces at: https://smith.langchain.com/\n")

    if not cv_content:
        raise ValueError("CV content is required but was not provided")

    if not callable(job_repository_factory):
        raise ValueError("job_repository_factory must be callable")

    workflow_config = {
        "configurable": {
            "job_repository_factory": job_repository_factory,
        }
    }

    workflow = create_workflow(workflow_config)

    initial_state: AgentState = {
        "job": job,
        "status": "started",
        "cv_context": cv_content,
    }

    final_state = workflow.invoke(initial_state)

    print(f"Workflow completed with status: {final_state['status']}")

    return final_state
