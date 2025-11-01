"""Print jobs node for the multiagent workflow.

This node processes and prints the list of jobs.
"""

from ..state import AgentState


def print_jobs_node(state: AgentState) -> AgentState:
    """
    Process and print the list of jobs.

    This is the main processing node that receives jobs and prints them.
    In the future, this can be expanded to perform more complex operations
    like filtering, analysis, or applying for jobs.

    Args:
        state: Current agent state containing the list of jobs

    Returns:
        Updated agent state with completion status
    """
    jobs = state["jobs"]

    print(f"\n{'='*60}")
    print(f"Processing {len(jobs)} jobs:")
    print(f"{'='*60}\n")

    for idx, job in enumerate(jobs, 1):
        print(f"Job #{idx}:")
        for key, value in job.items():
            print(f"  {key}: {value}")
        print()

    print(f"{'='*60}")
    print(f"Finished processing {len(jobs)} jobs")
    print(f"{'='*60}\n")

    return {
        "jobs": jobs,
        "status": "completed"
    }
