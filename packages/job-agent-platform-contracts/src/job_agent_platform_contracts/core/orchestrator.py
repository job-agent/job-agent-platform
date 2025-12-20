"""Interface for job agent orchestration."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Optional, Sequence

from job_scrapper_contracts import JobDict

from job_agent_platform_contracts.core.job_processing_result import JobProcessingResult
from job_agent_platform_contracts.core.pipeline_summary import PipelineSummary


class IJobAgentOrchestrator(ABC):
    """Contract for orchestrating job processing workflows."""

    @abstractmethod
    def get_cv_path(self, user_id: int) -> Path:
        """Return the storage path for the CV associated with the user."""

    @abstractmethod
    def upload_cv(self, user_id: int, file_path: str) -> None:
        """Process and store a CV for the user from the provided file path."""

    @abstractmethod
    def has_cv(self, user_id: int) -> bool:
        """Determine whether the user has a stored CV."""

    @abstractmethod
    def load_cv(self, user_id: int) -> str:
        """Load the processed CV content for the user."""

    @abstractmethod
    def scrape_jobs(
        self,
        min_salary: int = 4000,
        employment_location: str = "remote",
        days: Optional[int] = None,
        timeout: int = 30,
    ) -> list[JobDict]:
        """Retrieve job listings matching the provided filters.

        Args:
            min_salary: Minimum salary filter
            employment_location: Employment type or location filter
            days: Number of days to look back. If None, auto-calculates from latest
                  job in repository
            timeout: Request timeout in seconds
        """

    @abstractmethod
    def filter_jobs_list(self, jobs: Sequence[JobDict]) -> list[JobDict]:
        """Filter job listings according to the configured rules."""

    @abstractmethod
    def process_job(
        self,
        job: JobDict,
        cv_content: str,
    ) -> JobProcessingResult:
        """Execute processing workflows for a single job and return the results."""

    @abstractmethod
    def process_jobs_iterator(
        self,
        jobs: Sequence[JobDict],
        cv_content: str,
    ) -> Iterable[tuple[int, int, JobProcessingResult]]:
        """Yield processing results for each job alongside progress metadata."""

    @abstractmethod
    def run_complete_pipeline(
        self,
        user_id: int,
        min_salary: int = 4000,
        employment_location: str = "remote",
        days: Optional[int] = None,
        timeout: int = 30,
    ) -> PipelineSummary:
        """Execute the end-to-end job processing workflow and return summary data.

        Args:
            user_id: User identifier to load their CV
            min_salary: Minimum salary filter
            employment_location: Employment type or location filter
            days: Number of days to look back. If None, auto-calculates from latest
                  job in repository
            timeout: Request timeout in seconds
        """
