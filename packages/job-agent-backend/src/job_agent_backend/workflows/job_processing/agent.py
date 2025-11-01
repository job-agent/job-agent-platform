"""Main workflows system interface.

This module provides the public API for running the workflows system.
"""

import os

from job_scrapper_contracts import JobDict

from .job_processing import create_workflow
from .state import AgentState


def run_job_processing(job: JobDict, cv_content: str) -> None:
    """
    Run the workflows system on a single job.

    This is the main entry point for the workflows system. It accepts a single
    job dictionary and processes it through the langgraph workflow.

    Args:
        job: A single job dictionary to process
        cv_content: The CV content to match against the job

    Raises:
        ValueError: If cv_content is empty or None

    Example:
        >>> job = {"title": "Python Developer", "salary": 5000}
        >>> cv_content = "My CV content..."
        >>> run_job_processing(job, cv_content)
    """
    # Check if LangSmith tracing is enabled
    tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true"
    project_name = os.getenv("LANGCHAIN_PROJECT", "default")

    if tracing_enabled:
        print(f"🔍 LangSmith tracing enabled - Project: {project_name}")
        print("   View traces at: https://smith.langchain.com/\n")

    # Validate CV content
    if not cv_content:
        raise ValueError("CV content is required but was not provided")

    # Create the workflow
    workflow = create_workflow()

    # Initialize state for this job
    initial_state: AgentState = {"job": job, "status": "started", "cv_context": cv_content}

    # Run the workflow
    final_state = workflow.invoke(initial_state)

    print(f"Workflow completed with status: {final_state['status']}")
