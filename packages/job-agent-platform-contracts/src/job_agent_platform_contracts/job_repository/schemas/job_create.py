from typing import List, TypedDict

from .company_payload import CompanyPayload
from .location_payload import LocationPayload
from .salary_payload import SalaryPayload

ISODateString = str


class JobCreate(TypedDict, total=False):
    """Schema for creating a job including skill annotations.

    Required fields provide the core job record, optional fields extend the
    original job dictionary, and skill fields capture enrichment results from
    processing workflows.

    The skill fields use a 2D list format where:
    - The outer list represents AND relationships (all groups are required/preferred)
    - Inner lists represent OR relationships (alternatives within a group)

    Example: [["JavaScript", "Python"], ["React"]] means
    "(JavaScript OR Python) AND React"
    """

    job_id: int
    title: str
    url: str
    description: str
    company: CompanyPayload
    category: str
    date_posted: ISODateString
    valid_through: ISODateString
    employment_type: str

    salary: SalaryPayload
    experience_months: float
    location: LocationPayload
    industry: str

    must_have_skills: List[List[str]]
    nice_to_have_skills: List[List[str]]

    is_relevant: bool
    is_filtered: bool
