"""Print jobs node implementation."""

import logging

from ...state import AgentState
from .result import ProcessJobsResult

logger = logging.getLogger(__name__)


def print_jobs_node(state: AgentState) -> ProcessJobsResult:
    """
    Process and print a single job.

    This is the main processing node that receives a job and prints it.
    In the future, this can be expanded to perform more complex operations
    like filtering, analysis, or applying for jobs.

    Args:
        state: Current agent state containing a single job

    Returns:
        State update containing the completion status for the current job
    """
    job = state["job"]

    logger.info("Processing job")

    for key, value in job.items():
        logger.debug("  %s: %s", key, value)

    logger.info("Finished processing job")

    return {"status": "completed"}
