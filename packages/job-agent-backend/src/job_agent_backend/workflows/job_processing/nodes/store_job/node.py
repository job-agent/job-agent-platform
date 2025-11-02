"""Store job node implementation."""

from datetime import datetime
from typing import Optional

from jobs_repository.repository import JobRepository

from ...state import AgentState


def _map_job_dict_to_db_fields(job: dict) -> dict:
    """
    Map JobDict fields to database Job model fields.

    Args:
        job: JobDict from job_scrapper_contracts

    Returns:
        Dictionary with fields mapped to database schema
    """
    # Extract company name
    company_info = job.get("company", {})
    company_name = company_info.get("name", "Unknown") if isinstance(company_info, dict) else str(company_info)

    # Extract location info
    location_info = job.get("location", {})
    location_str = None
    is_remote = False
    if isinstance(location_info, dict):
        location_str = location_info.get("region")
        is_remote = location_info.get("is_remote", False)

    # Extract salary info
    salary_info = job.get("salary", {})
    salary_min = None
    salary_max = None
    salary_currency = "USD"
    if isinstance(salary_info, dict):
        salary_min = salary_info.get("min_value")
        salary_max = salary_info.get("max_value")
        salary_currency = salary_info.get("currency", "USD")

    # Parse datetime fields
    posted_at = None
    if "date_posted" in job and job["date_posted"]:
        try:
            posted_at = datetime.fromisoformat(job["date_posted"])
        except (ValueError, TypeError):
            pass

    expires_at = None
    if "valid_through" in job and job["valid_through"]:
        try:
            expires_at = datetime.fromisoformat(job["valid_through"])
        except (ValueError, TypeError):
            pass

    # Build the mapped dictionary
    db_fields = {
        "title": job.get("title", "Unknown"),
        "company": company_name,
        "location": location_str,
        "description": job.get("description"),
        "job_type": job.get("employment_type"),
        "experience_level": None,  # Not available in JobDict
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_currency": salary_currency,
        "external_id": str(job.get("job_id")) if "job_id" in job else None,
        "source": "job_scrapper",  # Default source
        "source_url": job.get("url"),
        "is_active": True,
        "is_remote": is_remote,
        "posted_at": posted_at,
        "expires_at": expires_at,
        "extra_data": {
            "category": job.get("category"),
            "industry": job.get("industry"),
            "experience_months": job.get("experience_months"),
        },
    }

    return db_fields


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
    job = state["job"]
    job_id = job.get("job_id")
    status = state.get("status", "in_progress")

    print(f"\n{'='*60}")
    print(f"Storing job to database (ID: {job_id})...")
    print(f"{'='*60}\n")

    # Get database session from state
    db_session = state.get("db_session")
    if not db_session:
        print("  ERROR: No database session available in state")
        print(f"{'='*60}\n")
        return {"status": "error"}

    try:
        # Create repository instance
        job_repo = JobRepository(db_session)

        # Map JobDict to database fields
        db_fields = _map_job_dict_to_db_fields(job)

        # Use upsert to avoid duplicates
        external_id = db_fields.get("external_id")
        source = db_fields.get("source", "job_scrapper")

        if external_id:
            stored_job = job_repo.upsert(external_id, source, db_fields)
            print(f"  Job stored successfully (DB ID: {stored_job.id})")
            print(f"  Title: {stored_job.title}")
            print(f"  Company: {stored_job.company}")
        else:
            # If no external_id, just create
            stored_job = job_repo.create(db_fields)
            print(f"  Job created successfully (DB ID: {stored_job.id})")

    except Exception as e:
        print(f"  ERROR storing job: {e}")
        print(f"{'='*60}\n")
        return {"status": "error"}

    print(f"{'='*60}")
    print(f"Finished storing job (ID: {job_id})")
    print(f"{'='*60}\n")

    return {"status": status}
