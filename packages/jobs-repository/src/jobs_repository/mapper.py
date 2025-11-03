"""Mapper service for transforming JobDict contract data to Job model format."""

from typing import Dict, Any
from dateutil import parser as date_parser

from job_scrapper_contracts import JobDict


class JobMapper:
    """
    Service for mapping JobDict contract data to Job model fields.

    This mapper handles:
    - Field name transformations (job_id -> external_id, url -> source_url, etc.)
    - Nested object extraction (company, location, etc.)
    - Data type conversions (ISO datetime strings -> datetime objects)
    - Flattening nested structures (salary dict -> separate fields)

    Note: This mapper only transforms data structure. It does NOT create any
    database entities. Entity creation is handled by the repository.
    """

    def map_to_model(self, job_data: JobDict | Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform JobDict contract data to Job model field dictionary.

        Args:
            job_data: Job data in JobDict format from contracts

        Returns:
            Dictionary with fields mapped to Job model format
        """
        mapped_data: Dict[str, Any] = {}

        # Map simple fields
        self._map_simple_fields(job_data, mapped_data)

        # Handle nested objects and relationships
        self._map_company(job_data, mapped_data)
        self._map_location(job_data, mapped_data)
        self._map_category(job_data, mapped_data)
        self._map_industry(job_data, mapped_data)

        # Handle complex fields
        self._map_salary(job_data, mapped_data)
        self._map_datetime_fields(job_data, mapped_data)

        return mapped_data

    def _map_simple_fields(
        self, job_data: JobDict | Dict[str, Any], mapped_data: Dict[str, Any]
    ) -> None:
        """Map simple scalar fields from JobDict to Job model."""
        mapped_data["title"] = job_data.get("title")
        mapped_data["description"] = job_data.get("description")
        mapped_data["external_id"] = str(job_data.get("job_id"))  # job_id -> external_id
        mapped_data["source_url"] = job_data.get("url")  # url -> source_url
        mapped_data["job_type"] = job_data.get("employment_type")  # employment_type -> job_type
        mapped_data["experience_months"] = job_data.get("experience_months")

        # Map skills arrays
        if must_have_skills := job_data.get("must_have_skills"):
            mapped_data["must_have_skills"] = must_have_skills
        if nice_to_have_skills := job_data.get("nice_to_have_skills"):
            mapped_data["nice_to_have_skills"] = nice_to_have_skills

    def _map_company(self, job_data: JobDict | Dict[str, Any], mapped_data: Dict[str, Any]) -> None:
        """Extract company name from nested object."""
        if company_data := job_data.get("company"):
            mapped_data["company_name"] = company_data["name"]

    def _map_location(
        self, job_data: JobDict | Dict[str, Any], mapped_data: Dict[str, Any]
    ) -> None:
        """Extract location from nested object."""
        if location_data := job_data.get("location"):
            if region := location_data.get("region"):
                mapped_data["location_region"] = region
            mapped_data["is_remote"] = location_data.get("is_remote", False)

    def _map_category(
        self, job_data: JobDict | Dict[str, Any], mapped_data: Dict[str, Any]
    ) -> None:
        """Extract category name."""
        if category_name := job_data.get("category"):
            mapped_data["category_name"] = category_name

    def _map_industry(
        self, job_data: JobDict | Dict[str, Any], mapped_data: Dict[str, Any]
    ) -> None:
        """Extract industry name."""
        if industry_name := job_data.get("industry"):
            mapped_data["industry_name"] = industry_name

    def _map_salary(self, job_data: JobDict | Dict[str, Any], mapped_data: Dict[str, Any]) -> None:
        """Flatten salary nested object into separate fields."""
        if salary_data := job_data.get("salary"):
            mapped_data["salary_currency"] = salary_data.get("currency", "USD")
            mapped_data["salary_min"] = salary_data.get("min_value")
            mapped_data["salary_max"] = salary_data.get("max_value")

    def _map_datetime_fields(
        self, job_data: JobDict | Dict[str, Any], mapped_data: Dict[str, Any]
    ) -> None:
        """Convert ISO datetime strings to datetime objects."""
        if date_posted := job_data.get("date_posted"):
            mapped_data["posted_at"] = date_parser.isoparse(date_posted)

        if valid_through := job_data.get("valid_through"):
            mapped_data["expires_at"] = date_parser.isoparse(valid_through)
