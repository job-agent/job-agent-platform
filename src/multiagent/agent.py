"""Main multiagent system interface.

This module provides the public API for running the multiagent system.
"""

from typing import List

from job_scrapper_contracts import JobDict

from .graph import create_workflow
from .state import AgentState


def run_multiagent_system(jobs: List[JobDict]) -> None:
    """
    Run the multiagent system on a list of jobs.

    This is the main entry point for the multiagent system. It accepts a list
    of job dictionaries, processes them through the langgraph workflow, and
    completes execution.

    Args:
        jobs: List of job dictionaries to process

    Example:
        >>> jobs = [{"title": "Python Developer", "salary": 5000}]
        >>> run_multiagent_system(jobs)
    """
    # Create the workflow
    workflow = create_workflow()

    # Initialize state
    initial_state: AgentState = {
        "jobs": jobs,
        "status": "started"
    }

    # Run the workflow
    final_state = workflow.invoke(initial_state)

    print(f"Workflow completed with status: {final_state['status']}")
