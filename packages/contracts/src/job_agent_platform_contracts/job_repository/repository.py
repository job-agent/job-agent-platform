"""Repository interface for job operations."""

from abc import ABC, abstractmethod
from typing import Optional

from job_scrapper_contracts import Job

from job_agent_platform_contracts.job_repository.schemas.job_create import JobCreate


class IJobRepository(ABC):
    """
    Interface for job repository operations.

    This interface defines the contract that all job repository implementations
    must follow, ensuring consistency across different storage backends.
    """

    @abstractmethod
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
        pass

    @abstractmethod
    def get_by_external_id(self, external_id: str, source: Optional[str] = None) -> Optional[Job]:
        """
        Get job by external ID and optional source.

        Args:
            external_id: External job identifier from the source platform
            source: Optional job source (e.g., 'LinkedIn', 'Indeed')

        Returns:
            Job entity if found, None otherwise
        """
        pass

    @abstractmethod
    def has_active_job_with_title_and_company(self, title: str, company_name: str) -> bool:
        """
        Determine if an active job exists for the given title and company.

        Args:
            title: Job title to match
            company_name: Company name to match

        Returns:
            True when an active job exists, False otherwise
        """
        pass
