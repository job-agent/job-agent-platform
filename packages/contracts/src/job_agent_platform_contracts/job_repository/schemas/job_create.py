from typing import TypedDict, List


class JobCreate(TypedDict, total=False):
    """Schema for creating a job with all fields including skills.

    This schema extends the basic job data with additional fields like
    must_have_skills and nice_to_have_skills that are populated during
    job processing workflows.
    """

    # Required fields (when total=False, these are still effectively required by business logic)
    job_id: int
    title: str
    url: str
    description: str
    company: dict  # CompanyDict from job_scrapper_contracts
    category: str
    date_posted: str  # ISO format datetime string
    valid_through: str  # ISO format datetime string
    employment_type: str

    # Optional fields from JobDict
    salary: dict  # SalaryDict from job_scrapper_contracts
    experience_months: float
    location: dict  # LocationDict from job_scrapper_contracts
    industry: str

    # Additional fields for job creation with skills
    must_have_skills: List[str]
    nice_to_have_skills: List[str]
