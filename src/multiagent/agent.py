"""Main multiagent system interface.

This module provides the public API for running the multiagent system.
"""

import os

from job_scrapper_contracts import JobDict

from .graph import create_workflow
from .state import AgentState


def run_multiagent_system(job: JobDict) -> None:
    """
    Run the multiagent system on a single job.

    This is the main entry point for the multiagent system. It accepts a single
    job dictionary and processes it through the langgraph workflow.

    Args:
        job: A single job dictionary to process

    Example:
        >>> job = {"title": "Python Developer", "salary": 5000}
        >>> run_multiagent_system(job)
    """
    # Check if LangSmith tracing is enabled
    tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true"
    project_name = os.getenv("LANGCHAIN_PROJECT", "default")

    if tracing_enabled:
        print(f"🔍 LangSmith tracing enabled - Project: {project_name}")
        print(f"   View traces at: https://smith.langchain.com/\n")

    # Create the workflow
    workflow = create_workflow()

    # Initialize state for this job
    initial_state: AgentState = {
        "job": job,
        "status": "started"
    }

    # Run the workflow
    final_state = workflow.invoke(initial_state)

    print(f"Workflow completed with status: {final_state['status']}")
