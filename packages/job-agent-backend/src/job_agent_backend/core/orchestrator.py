"""Core orchestration logic for job processing.

This module contains the business logic for scraping, filtering, and processing jobs.
It can be used by any interface (CLI, Telegram, Web, etc.).
CV management is delegated to CVManager.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Iterator, Optional, Sequence, cast

from cvs_repository import CVRepository
from job_scrapper_contracts import JobDict
from job_agent_platform_contracts import (
    ICVRepository,
    IJobRepository,
    IJobAgentOrchestrator,
    JobProcessingResult,
    PipelineSummary,
)
from job_agent_backend.cv_loader import ICVLoader
from job_agent_backend.filter_service import IFilterService
from job_agent_backend.messaging import IScrapperClient
from job_agent_backend.workflows import run_job_processing, run_pii_removal
from job_agent_backend.workflows.job_processing.state import AgentState
from job_agent_backend.core.cv_manager import CVManager


# Maximum number of days to look back when auto-calculating posted_after
MAX_AUTO_DAYS = 5


CVRepositoryFactory = Callable[[str | Path], ICVRepository]


class JobAgentOrchestrator(IJobAgentOrchestrator):
    """Orchestrates the complete job processing pipeline.

    This class provides a clean interface for running the job agent workflow
    from any entry point (CLI, Telegram bot, API, etc.). CV operations are
    delegated to CVManager for separation of concerns.
    """

    def __init__(
        self,
        cv_repository_class: CVRepositoryFactory,
        cv_loader: ICVLoader,
        job_repository_factory: Callable[[], IJobRepository],
        scrapper_manager: IScrapperClient,
        filter_service: IFilterService,
        database_initializer: Callable[[], None],
        logger: Optional[Callable[[str], None]] = None,
    ):
        """Initialize the orchestrator.

        Args:
            logger: Optional logging function to report progress.
                   If None, will use print().
            cv_repository_class: CV repository class to use for creating instances.
                                Defaults to CVRepository for backward compatibility.
            cv_loader: Optional loader implementation for reading CV content.
                        Defaults to the built-in PDF/text loader.
            job_repository_factory: Factory for creating job repository instances.
                                     Required for persisting workflow results.
            scrapper_manager: Optional scrapper manager instance.
                            If None, will create a new ScrapperManager().
            filter_service: Optional filter service instance. If not provided, the
                            default configuration-based implementation is used.
        """
        self.logger: Callable[[str], None] = logger or print
        repository_factory = CVRepository if cv_repository_class is None else cv_repository_class
        if job_repository_factory is None:
            raise ValueError("job_repository_factory must be provided")
        self.job_repository_factory: Callable[[], IJobRepository] = job_repository_factory
        self.scrapper_manager: IScrapperClient = scrapper_manager
        self.filter_service: IFilterService = filter_service
        self.database_initializer: Callable[[], None] = database_initializer

        # Delegate CV operations to CVManager
        self._cv_manager = CVManager(
            cv_repository_class=repository_factory,
            cv_loader=cv_loader,
            pii_removal_func=run_pii_removal,
            logger=self.logger,
        )

    def get_cv_path(self, user_id: int) -> Path:
        """Get the storage path for a user's CV.

        Args:
            user_id: User identifier (e.g., Telegram user ID)

        Returns:
            Path object for the user's CV file
        """
        return self._cv_manager.get_cv_path(user_id)

    def upload_cv(self, user_id: int, file_path: str) -> None:
        """Upload and process a CV file for a user.

        Automatically detects file type and processes accordingly.
        Supports PDF and text files.

        Args:
            user_id: User identifier
            file_path: Path to CV file (PDF or text)

        Raises:
            ValueError: If file format is unsupported or processing fails
        """
        self._cv_manager.upload_cv(user_id, file_path)

    def has_cv(self, user_id: int) -> bool:
        """Check if a user has uploaded a CV.

        Args:
            user_id: User identifier

        Returns:
            True if user has a CV, False otherwise
        """
        return self._cv_manager.has_cv(user_id)

    def load_cv(self, user_id: int) -> str:
        """Load CV content for a user from repository.

        The CV is already cleaned of PII (done during upload).

        Args:
            user_id: User identifier

        Returns:
            CV content (already cleaned of PII)

        Raises:
            ValueError: If CV is not found or cannot be loaded
        """
        return self._cv_manager.load_cv(user_id)

    def _calculate_posted_after(self, days: Optional[int]) -> datetime:
        """Calculate the posted_after datetime based on days parameter.

        If days is provided, returns now - days.
        If days is None, queries the job repository for the latest job timestamp
        and returns that, capped at MAX_AUTO_DAYS.

        Args:
            days: Number of days to look back, or None for auto-calculation

        Returns:
            UTC-aware datetime for posted_after filter
        """
        now = datetime.now(timezone.utc)

        if days is not None:
            return now - timedelta(days=days)

        # Auto-calculate from repository
        repository = self.job_repository_factory()
        latest_updated_at = repository.get_latest_updated_at()

        if latest_updated_at is None:
            # No jobs in repository, use MAX_AUTO_DAYS as default
            return now - timedelta(days=MAX_AUTO_DAYS)

        # Normalize timezone-naive datetime to UTC
        if latest_updated_at.tzinfo is None:
            latest_updated_at = latest_updated_at.replace(tzinfo=timezone.utc)

        # Cap at MAX_AUTO_DAYS
        max_lookback = now - timedelta(days=MAX_AUTO_DAYS)
        if latest_updated_at < max_lookback:
            return max_lookback

        return latest_updated_at

    def scrape_jobs(
        self,
        min_salary: Optional[int] = 4000,
        employment_location: Optional[str] = "remote",
        days: Optional[int] = None,
        timeout: int = 30,
    ) -> list[JobDict]:
        """Scrape jobs using the scrapper service.

        Automatically paginates through all pages until reaching the date cutoff.

        Args:
            min_salary: Minimum salary filter
            employment_location: Employment type or location filter
            days: Number of days to look back. If None, auto-calculates from latest
                  job in repository (capped at MAX_AUTO_DAYS)
            timeout: Request timeout in seconds

        Returns:
            List of job dictionaries
        """
        posted_after = self._calculate_posted_after(days)
        self.logger("Scraping jobs...")
        all_jobs = []
        for batch_jobs in self.scrapper_manager.scrape_jobs_streaming(
            min_salary=min_salary,
            employment_location=employment_location,
            posted_after=posted_after,
            timeout=timeout,
        ):
            all_jobs.extend(batch_jobs)

        self.logger(f"Scraped {len(all_jobs)} jobs")
        return all_jobs

    def scrape_jobs_streaming(
        self,
        min_salary: Optional[int] = 4000,
        employment_location: Optional[str] = "remote",
        days: Optional[int] = None,
        timeout: int = 30,
    ) -> Iterator[tuple[list[JobDict], int]]:
        """Scrape jobs using the scrapper service, yielding batches as they arrive.

        Automatically paginates through all pages until reaching the date cutoff,
        yielding each batch as soon as it's received from the scrapper.

        Args:
            min_salary: Minimum salary filter
            employment_location: Employment type or location filter
            days: Number of days to look back. If None, auto-calculates from latest
                  job in repository (capped at MAX_AUTO_DAYS)
            timeout: Request timeout in seconds

        Yields:
            tuple[list[JobDict], int]: (batch_jobs, total_jobs_so_far)
        """
        posted_after = self._calculate_posted_after(days)
        self.logger("Starting streaming job scrape...")
        total_jobs = 0

        for batch_jobs in self.scrapper_manager.scrape_jobs_streaming(
            min_salary=min_salary,
            employment_location=employment_location,
            posted_after=posted_after,
            timeout=timeout,
        ):
            total_jobs += len(batch_jobs)
            self.logger(f"Scraped batch: {len(batch_jobs)} jobs (total: {total_jobs})")
            yield batch_jobs, total_jobs

        self.logger(f"Completed scraping: {total_jobs} total jobs")

    def filter_jobs_list(self, jobs: Sequence[JobDict]) -> list[JobDict]:
        """Filter jobs based on configuration and save rejected jobs.

        Uses filter_with_rejected to get both passed and rejected jobs.
        Rejected jobs are stored with is_filtered=True, is_relevant=False
        so they can be included in existing_urls for future scrapes.

        Args:
            jobs: List of job dictionaries

        Returns:
            Filtered list of jobs that passed all criteria
        """
        self.logger("Filtering jobs...")
        passed_jobs, rejected_jobs = self.filter_service.filter_with_rejected(list(jobs))
        self.logger(f"Filtered jobs: {len(passed_jobs)}/{len(jobs)} jobs passed")

        # Save rejected jobs to repository with is_filtered=True
        if rejected_jobs:
            repository = self.job_repository_factory()
            saved_count = repository.save_filtered_jobs(rejected_jobs)
            self.logger(f"Saved {saved_count} filtered jobs to repository")

        return passed_jobs

    def process_job(
        self,
        job: JobDict,
        cv_content: str,
    ) -> JobProcessingResult:
        """Process a single job with the workflows system.

        Args:
            job: Job dictionary to process
            cv_content: Cleaned CV content

        Returns:
            Dictionary containing processing results:
            - is_relevant: Whether the job is relevant to the candidate
            - extracted_must_have_skills: List of must-have skills (for relevant jobs)
            - extracted_nice_to_have_skills: List of nice-to-have skills (for relevant jobs)
            - status: Final workflow status
            - job: Original job dictionary
        """
        result: AgentState = run_job_processing(
            job,
            cv_content,
            job_repository_factory=self.job_repository_factory,
        )
        return cast(JobProcessingResult, result)

    def process_jobs_iterator(
        self,
        jobs: Sequence[JobDict],
        cv_content: str,
    ) -> Iterator[tuple[int, int, JobProcessingResult]]:
        """Process jobs one at a time, yielding results as they complete.

        Useful for progress reporting in interactive contexts.

        Args:
            jobs: List of job dictionaries to process
            cv_content: Cleaned CV content

        Yields:
            Tuple of (job_index, total_jobs, result_dict) for each processed job
        """
        for idx, job in enumerate(jobs, 1):
            result = self.process_job(job, cv_content)
            yield idx, len(jobs), result

    def run_complete_pipeline(
        self,
        user_id: int,
        min_salary: Optional[int] = 4000,
        employment_location: Optional[str] = "remote",
        days: Optional[int] = None,
        timeout: int = 30,
    ) -> PipelineSummary:
        """Run the complete job processing pipeline.

        This is the main entry point that:
        1. Initializes database (creates tables if needed)
        2. Scrapes jobs (automatically paginates until date cutoff)
        3. Filters unsuitable jobs
        4. Loads CV from repository (already PII-free)
        5. Processes each job with workflows and stores relevant ones

        Args:
            user_id: User identifier to load their CV
            min_salary: Minimum salary filter
            employment_location: Employment type or location filter
            days: Number of days to look back. If None, auto-calculates from latest
                  job in repository (capped at MAX_AUTO_DAYS)
            timeout: Request timeout in seconds

        Returns:
            Dictionary with pipeline results and statistics

        Raises:
            ValueError: If user CV is not found or cannot be loaded
        """
        self.logger("Initializing database...")
        try:
            self.database_initializer()
            self.logger("Database initialized successfully")
        except Exception as e:
            self.logger(f"Warning: Database initialization failed: {e}")
            self.logger("Continuing without database storage...")

        jobs = self.scrape_jobs(min_salary, employment_location, days, timeout)

        filtered_jobs = self.filter_jobs_list(jobs)

        cleaned_cv = self.load_cv(user_id)

        self.logger(f"Processing {len(filtered_jobs)} jobs with workflows system...")

        for idx, job in enumerate(filtered_jobs, 1):
            self.logger(f"\nProcessing job {idx}/{len(filtered_jobs)}")
            self.process_job(job, cleaned_cv)

        results: PipelineSummary = {
            "total_scraped": len(jobs),
            "total_filtered": len(filtered_jobs),
            "total_processed": len(filtered_jobs),
        }

        self.logger(f"\nPipeline completed - Processed {len(filtered_jobs)} jobs")
        return results
