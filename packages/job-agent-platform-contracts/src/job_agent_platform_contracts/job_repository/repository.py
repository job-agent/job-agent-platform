"""Repository interface for job operations."""

from datetime import datetime
from typing import List, Optional, Protocol, runtime_checkable

from job_scrapper_contracts import Job, JobDict

from job_agent_platform_contracts.job_repository.schemas.job_create import JobCreate


@runtime_checkable
class IJobRepository(Protocol):
    """
    Interface for job repository operations.

    This interface defines the contract that all job repository implementations
    must follow, ensuring consistency across different storage backends.
    """

    def create(self, job_data: JobCreate) -> Job:
        """
        Create a new job from a `JobCreate` payload.

        Args:
            job_data: Typed dictionary describing the job to persist.

        Returns:
            Created job entity

        Raises:
            JobAlreadyExistsError: If job with same external_id already exists
            ValidationError: If data validation fails
            TransactionError: If database transaction fails
        """
        ...

    def get_by_external_id(self, external_id: str, source: Optional[str] = None) -> Optional[Job]:
        """
        Get job by external ID and optional source.

        Args:
            external_id: External job identifier from the source platform
            source: Optional job source (e.g., 'LinkedIn', 'Indeed')

        Returns:
            Job entity if found, None otherwise
        """
        ...

    def has_active_job_with_title_and_company(self, title: str, company_name: str) -> bool:
        """
        Determine if an active job exists for the given title and company.

        Args:
            title: Job title to match
            company_name: Company name to match

        Returns:
            True when an active job exists, False otherwise
        """
        ...

    def get_existing_urls_by_source(self, source: str, days: Optional[int] = None) -> list[str]:
        """
        Get existing job URLs for a given source, optionally filtered by time window.

        Args:
            source: Job source (e.g., 'djinni', 'linkedin')
            days: Optional number of days to look back. If provided, only returns URLs
                  for jobs posted within the last N days. If None, returns all URLs.

        Returns:
            List of URLs for jobs from the specified source
        """
        ...

    def save_filtered_jobs(self, jobs: List[JobDict]) -> int:
        """
        Save multiple filtered jobs in a batch operation.

        Filtered jobs are stored with is_filtered=True and is_relevant=False
        so they can be included in existing_urls for future scrapes.

        Args:
            jobs: List of job dictionaries that were rejected by pre-LLM filtering

        Returns:
            Count of jobs that were successfully saved (excluding duplicates)
        """
        ...

    def get_latest_updated_at(self) -> Optional[datetime]:
        """
        Get the most recent updated_at timestamp from all jobs.

        This method is used to auto-calculate the search date range when
        the days parameter is not explicitly provided. It returns the latest
        updated_at timestamp from the jobs table.

        Returns:
            The latest updated_at datetime if jobs exist, None otherwise.
        """
        ...
