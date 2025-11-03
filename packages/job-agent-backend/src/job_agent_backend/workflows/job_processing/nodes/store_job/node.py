"""Store job node implementation."""

from job_scrapper_contracts import JobDict

from jobs_repository.repository import JobRepository
from jobs_repository.schemas import JobCreate

from ...state import AgentState


def store_job_node(state: AgentState) -> AgentState:
    """
    Store a relevant job to the database.

    This node takes a job from the workflow state and stores it in the database
    using the JobRepository. Only relevant jobs reach this node due to
    conditional routing in the workflow.

    Args:
        state: Current agent state containing job and db_session

    Returns:
        Updated agent state with storage status
    """
    job: JobDict = state["job"]
    job_id = job.get("job_id")
    status = state.get("status", "in_progress")

    print(f"\n{'='*60}")
    print(f"Storing job to database (ID: {job_id})...")
    print(f"{'='*60}\n")

    # Get database session from state
    db_session = state.get("db_session")
    if not db_session:
        print("  ERROR: No database session available in state")
        print(f"  State keys: {list(state.keys())}")
        print("  HINT: Make sure DATABASE_URL is set and database is running")
        print("  HINT: Ensure db_session is passed to run_job_processing()")
        print(f"{'='*60}\n")
        return {"status": status}

    try:
        # Create repository instance
        job_repo = JobRepository(db_session)

        # Create JobCreate dict with job data and extracted skills
        job_create_data: JobCreate = {**job}  # type: ignore

        # Add extracted skills from state to the job data
        if extracted_must_have_skills := state.get("extracted_must_have_skills"):
            job_create_data["must_have_skills"] = extracted_must_have_skills
            print(f"  Added {len(extracted_must_have_skills)} must-have skills")

        if extracted_nice_to_have_skills := state.get("extracted_nice_to_have_skills"):
            job_create_data["nice_to_have_skills"] = extracted_nice_to_have_skills
            print(f"  Added {len(extracted_nice_to_have_skills)} nice-to-have skills")

        stored_job = job_repo.create(job_create_data)
        print(f"  Job created successfully (DB ID: {stored_job.id})")

    except Exception as e:
        print(f"  ERROR storing job: {e}")
        print(f"{'='*60}\n")
        return {"status": "error"}

    print(f"{'='*60}")
    print(f"Finished storing job (ID: {job_id})")
    print(f"{'='*60}\n")

    return {"status": status}
