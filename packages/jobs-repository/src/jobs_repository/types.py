"""Type definitions for jobs repository."""

from typing import TypedDict, Optional
from datetime import datetime


class JobModelDict(TypedDict, total=False):
    """Type-safe dictionary for Job model creation.

    This represents the data structure used to create Job model instances.

    The skill fields use a 2D list format where:
    - The outer list represents AND relationships (all groups are required/preferred)
    - Inner lists represent OR relationships (alternatives within a group)
    """

    title: str
    description: Optional[str]
    must_have_skills: Optional[list[list[str]]]
    nice_to_have_skills: Optional[list[list[str]]]

    company_id: Optional[int]
    company_name: Optional[str]

    location_id: Optional[int]
    location_region: Optional[str]

    category_id: Optional[int]
    category_name: Optional[str]

    industry_id: Optional[int]
    industry_name: Optional[str]

    job_type: Optional[str]
    experience_months: Optional[int]

    salary_min: Optional[float]
    salary_max: Optional[float]
    salary_currency: Optional[str]

    external_id: str
    source: Optional[str]
    source_url: Optional[str]

    is_remote: bool
    is_relevant: bool
    is_filtered: bool
    posted_at: Optional[datetime]
    expires_at: Optional[datetime]


class JobSerializedDict(TypedDict, total=False):
    """Type-safe dictionary for serialized Job data.

    This represents the structure returned when serializing a Job model to dict.

    The skill fields use a 2D list format where:
    - The outer list represents AND relationships (all groups are required/preferred)
    - Inner lists represent OR relationships (alternatives within a group)
    """

    id: int
    title: str
    description: Optional[str]
    must_have_skills: Optional[list[list[str]]]
    nice_to_have_skills: Optional[list[list[str]]]

    company_id: Optional[int]
    company_name: Optional[str]

    location_id: Optional[int]
    location_region: Optional[str]

    category_id: Optional[int]
    category_name: Optional[str]

    industry_id: Optional[int]
    industry_name: Optional[str]

    job_type: Optional[str]
    experience_months: Optional[int]

    salary_min: Optional[float]
    salary_max: Optional[float]
    salary_currency: Optional[str]

    external_id: Optional[str]
    source: Optional[str]
    source_url: Optional[str]

    is_remote: bool
    is_relevant: bool
    is_filtered: bool
    posted_at: Optional[str]
    expires_at: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
