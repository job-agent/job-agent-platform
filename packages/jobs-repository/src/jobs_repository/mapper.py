"""Mapper service for transforming JobDict contract data to Job model format."""

from typing import TYPE_CHECKING, Any, List, Optional, cast
from dateutil import parser as date_parser

from job_scrapper_contracts import JobDict
from jobs_repository.interfaces import IJobMapper
from jobs_repository.types import JobModelDict, JobSerializedDict

if TYPE_CHECKING:
    from jobs_repository.models import Job


class JobMapper(IJobMapper):
    """
    Service for bidirectional mapping between Job model and contract data.

    This mapper handles:
    - Field name transformations (job_id -> external_id, url -> source_url, etc.)
    - Nested object extraction (company, location, etc.)
    - Data type conversions (ISO datetime strings -> datetime objects)
    - Flattening/expanding nested structures (salary dict -> separate fields)
    - Serialization from Job model to dictionary representation

    Note: This mapper only transforms data structure. It does NOT create any
    database entities. Entity creation is handled by the repository.
    """

    def map_to_model(self, job_data: JobDict) -> JobModelDict:
        """
        Transform JobDict contract data to Job model field dictionary.

        Args:
            job_data: Job data in JobDict format from job-agent-platform-contracts

        Returns:
            Type-safe dictionary with fields mapped to Job model format
        """
        mapped_data: JobModelDict = {}

        self._map_simple_fields(job_data, mapped_data)

        self._map_company(job_data, mapped_data)
        self._map_location(job_data, mapped_data)
        self._map_category(job_data, mapped_data)
        self._map_industry(job_data, mapped_data)

        self._map_salary(job_data, mapped_data)
        self._map_datetime_fields(job_data, mapped_data)

        return mapped_data

    def _map_simple_fields(self, job_data: JobDict, mapped_data: JobModelDict) -> None:
        """Map simple scalar fields from JobDict to Job model."""
        if "title" in job_data:
            mapped_data["title"] = job_data["title"]
        if "job_id" in job_data:
            mapped_data["external_id"] = str(job_data["job_id"])

        mapped_data["description"] = job_data.get("description")
        mapped_data["source_url"] = job_data.get("url")
        mapped_data["source"] = job_data.get("source")
        mapped_data["job_type"] = job_data.get("employment_type")
        experience = job_data.get("experience_months")
        mapped_data["experience_months"] = int(experience) if experience is not None else None

        # These fields may be added dynamically, not in JobDict contract
        job_data_any: Any = job_data
        if (must_have_skills := job_data_any.get("must_have_skills")) is not None:
            mapped_data["must_have_skills"] = must_have_skills
        if (nice_to_have_skills := job_data_any.get("nice_to_have_skills")) is not None:
            mapped_data["nice_to_have_skills"] = nice_to_have_skills

        mapped_data["is_relevant"] = job_data_any.get("is_relevant", True)
        mapped_data["is_filtered"] = job_data_any.get("is_filtered", False)

    def _map_company(self, job_data: JobDict, mapped_data: JobModelDict) -> None:
        """Extract company name from nested object."""
        if company_data := job_data.get("company"):
            mapped_data["company_name"] = company_data["name"]

    def _map_location(self, job_data: JobDict, mapped_data: JobModelDict) -> None:
        """Extract location from nested object."""
        if location_data := job_data.get("location"):
            if region := location_data.get("region"):
                mapped_data["location_region"] = region
            mapped_data["is_remote"] = location_data.get("is_remote", False)

    def _map_category(self, job_data: JobDict, mapped_data: JobModelDict) -> None:
        """Extract category name."""
        if category_name := job_data.get("category"):
            mapped_data["category_name"] = category_name

    def _map_industry(self, job_data: JobDict, mapped_data: JobModelDict) -> None:
        """Extract industry name."""
        if industry_name := job_data.get("industry"):
            mapped_data["industry_name"] = industry_name

    def _map_salary(self, job_data: JobDict, mapped_data: JobModelDict) -> None:
        """Flatten salary nested object into separate fields."""
        if salary_data := job_data.get("salary"):
            mapped_data["salary_currency"] = salary_data.get("currency", "USD")
            mapped_data["salary_min"] = salary_data.get("min_value")
            mapped_data["salary_max"] = salary_data.get("max_value")

    def _map_datetime_fields(self, job_data: JobDict, mapped_data: JobModelDict) -> None:
        """Convert ISO datetime strings to datetime objects."""
        if date_posted := job_data.get("date_posted"):
            mapped_data["posted_at"] = date_parser.isoparse(date_posted)

        if valid_through := job_data.get("valid_through"):
            mapped_data["expires_at"] = date_parser.isoparse(valid_through)

    def map_from_model(self, job: "Job") -> JobSerializedDict:
        """
        Transform Job model to dictionary representation.

        Args:
            job: Job model instance

        Returns:
            Type-safe dictionary with all job fields serialized
        """
        # SQLAlchemy model attributes are typed as Column[T] but return T at runtime
        result: JobSerializedDict = {
            "id": cast(int, job.id),
            "title": cast(str, job.title),
            "company_id": cast(Optional[int], job.company_id),
            "company_name": job.company_rel.name if job.company_rel else None,
            "location_id": cast(Optional[int], job.location_id),
            "location_region": job.location_rel.region if job.location_rel else None,
            "category_id": cast(Optional[int], job.category_id),
            "category_name": job.category_rel.name if job.category_rel else None,
            "industry_id": cast(Optional[int], job.industry_id),
            "industry_name": job.industry_rel.name if job.industry_rel else None,
            "description": cast(Optional[str], job.description),
            "must_have_skills": cast(Optional[List[str]], job.must_have_skills),
            "nice_to_have_skills": cast(Optional[List[str]], job.nice_to_have_skills),
            "job_type": cast(Optional[str], job.job_type),
            "experience_months": cast(Optional[int], job.experience_months),
            "salary_min": cast(Optional[float], job.salary_min),
            "salary_max": cast(Optional[float], job.salary_max),
            "salary_currency": cast(Optional[str], job.salary_currency),
            "external_id": cast(Optional[str], job.external_id),
            "source": cast(Optional[str], job.source),
            "source_url": cast(Optional[str], job.source_url),
            "is_remote": cast(bool, job.is_remote),
            "is_relevant": cast(bool, job.is_relevant),
            "is_filtered": cast(bool, job.is_filtered),
            "posted_at": job.posted_at.isoformat() if job.posted_at else None,
            "expires_at": job.expires_at.isoformat() if job.expires_at else None,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        }
        return result
