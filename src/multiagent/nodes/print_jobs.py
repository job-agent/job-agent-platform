"""Print jobs node for the multiagent workflow.

This node processes and prints a single job.
"""

from ..state import AgentState


def print_jobs_node(state: AgentState) -> AgentState:
    """
    Process and print a single job.

    This is the main processing node that receives a job and prints it.
    In the future, this can be expanded to perform more complex operations
    like filtering, analysis, or applying for jobs.

    Args:
        state: Current agent state containing a single job

    Returns:
        Updated agent state with completion status
    """
    job = state["job"]

    print(f"\n{'='*60}")
    print(f"Processing job:")
    print(f"{'='*60}\n")

    for key, value in job.items():
        print(f"  {key}: {value}")
    print()

    print(f"{'='*60}")
    print(f"Finished processing job")
    print(f"{'='*60}\n")

    return {
        "job": job,
        "status": "completed"
    }
