"""Store job node implementation."""

from typing import Callable

from job_agent_platform_contracts import IJobRepository
from job_scrapper_contracts import JobDict

from job_agent_platform_contracts.job_repository.schemas import JobCreate

from ...state import AgentState, AgentStateUpdate


def create_store_job_node(
    job_repository_factory: Callable[[], IJobRepository],
) -> Callable:
    """
    Factory function to create a store_job_node with injected dependencies.

    Args:
        job_repository_factory: Factory used to create job repository instances

    Returns:
        Configured store_job_node function
    """

    def store_job_node(state: AgentState) -> AgentStateUpdate:
        """
        Store a relevant job to the database.

        This node takes a job from the workflow state and stores it in the database
        using the JobRepository. Only relevant jobs reach this node due to
        conditional routing in the workflow.

        Args:
            state: Current agent state containing job details

        Returns:
            State update containing the persistence status for the job
        """
        job: JobDict = state["job"]
        job_id = job.get("job_id")
        status = state.get("status", "in_progress")

        print(f"\n{'=' * 60}")
        print(f"Storing job to database (ID: {job_id})...")
        print(f"{'=' * 60}\n")

        try:
            job_repo = job_repository_factory()

            job_create_data: JobCreate = {**job}

            # Pass is_relevant from workflow state (defaults to True for backwards compatibility)
            job_create_data["is_relevant"] = state.get("is_relevant", True)

            if (extracted_must_have_skills := state.get("extracted_must_have_skills")) is not None:
                job_create_data["must_have_skills"] = extracted_must_have_skills
                print(f"  Added {len(extracted_must_have_skills)} must-have skills")

            if (
                extracted_nice_to_have_skills := state.get("extracted_nice_to_have_skills")
            ) is not None:
                job_create_data["nice_to_have_skills"] = extracted_nice_to_have_skills
                print(f"  Added {len(extracted_nice_to_have_skills)} nice-to-have skills")

            stored_job = job_repo.create(job_create_data)
            print(f"  Job created successfully (DB ID: {stored_job.id})")

        except Exception as e:
            print(f"  ERROR storing job: {e}")
            print(f"{'=' * 60}\n")
            return {"status": "error"}

        print(f"{'=' * 60}")
        print(f"Finished storing job (ID: {job_id})")
        print(f"{'=' * 60}\n")

        return {"status": status}

    return store_job_node
