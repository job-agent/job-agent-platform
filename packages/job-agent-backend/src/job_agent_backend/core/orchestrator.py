"""Core orchestration logic for job processing.

This module contains the business logic for scraping, filtering, and processing jobs.
It can be used by any interface (CLI, Telegram, Web, etc.).
"""

from datetime import datetime
from pathlib import Path
from typing import Callable, Iterator, Optional, Protocol, Sequence, cast

from cvs_repository import CVRepository
from job_scrapper_contracts import JobDict
from job_agent_platform_contracts import (
    ICVRepository,
    IJobRepository,
    IJobAgentOrchestrator,
    JobProcessingResult,
    PipelineSummary,
)
from job_agent_backend.contracts import ICVLoader, IFilterService
from job_agent_backend.workflows import run_job_processing, run_pii_removal
from job_agent_backend.workflows.job_processing.state import AgentState


CVRepositoryFactory = Callable[[str | Path], ICVRepository]


class ScrapperManagerProtocol(Protocol):
    def scrape_jobs_as_dicts(
        self,
        min_salary: Optional[int],
        employment_location: Optional[str],
        posted_after: Optional[datetime],
        timeout: int,
    ) -> list[JobDict]: ...


class JobAgentOrchestrator(IJobAgentOrchestrator):
    """Orchestrates the complete job processing pipeline.

    This class provides a clean interface for running the job agent workflow
    from any entry point (CLI, Telegram bot, API, etc.).
    """

    def __init__(
        self,
        cv_repository_class: CVRepositoryFactory,
        cv_loader: ICVLoader,
        job_repository_factory: Callable[[], IJobRepository],
        scrapper_manager: ScrapperManagerProtocol,
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
        repository_factory = cv_repository_class or CVRepository
        self.cv_repository_class: CVRepositoryFactory = repository_factory
        self.cv_loader: ICVLoader = cv_loader
        if job_repository_factory is None:
            raise ValueError("job_repository_factory must be provided")
        self.job_repository_factory: Callable[[], IJobRepository] = job_repository_factory
        self.scrapper_manager: ScrapperManagerProtocol = scrapper_manager
        self.filter_service: IFilterService = filter_service
        self.database_initializer: Callable[[], None] = database_initializer

    def get_cv_path(self, user_id: int) -> Path:
        """Get the storage path for a user's CV.

        Args:
            user_id: User identifier (e.g., Telegram user ID)

        Returns:
            Path object for the user's CV file
        """
        package_root = Path(__file__).parent.parent.parent
        cv_dir = package_root / "data" / "cvs"
        cv_dir.mkdir(parents=True, exist_ok=True)
        return cv_dir / f"cv_{user_id}.txt"

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
        file_path_lower = file_path.lower()

        if file_path_lower.endswith(".pdf"):
            self.logger(f"Processing PDF CV for user {user_id}")
            cv_content = self.cv_loader.load_from_pdf(file_path)
        elif file_path_lower.endswith(".txt"):
            self.logger(f"Processing text CV for user {user_id}")
            cv_content = self.cv_loader.load_from_text(file_path)
        else:
            extension = Path(file_path).suffix
            raise ValueError(f"Unsupported file format: {extension}. Supported formats: .pdf, .txt")

        if not cv_content:
            raise ValueError("Failed to extract content from CV file")

        self.logger(f"Removing PII from CV for user {user_id}")
        cleaned_cv_content = run_pii_removal(cv_content)
        self.logger(f"PII removed from CV for user {user_id}")

        cv_path = self.get_cv_path(user_id)
        cv_repository = self.cv_repository_class(cv_path)
        cv_repository.create(cleaned_cv_content)
        self.logger(f"CV saved for user {user_id}")

    def has_cv(self, user_id: int) -> bool:
        """Check if a user has uploaded a CV.

        Args:
            user_id: User identifier

        Returns:
            True if user has a CV, False otherwise
        """
        try:
            cv_path = self.get_cv_path(user_id)
            cv_repository = self.cv_repository_class(cv_path)
            return cv_repository.find() is not None
        except Exception:
            return False

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
        self.logger(f"Loading CV from repository for user {user_id}")
        cv_path = self.get_cv_path(user_id)
        cv_repository = self.cv_repository_class(cv_path)
        cv_content = cv_repository.find()

        if not cv_content:
            raise ValueError(f"CV not found for user {user_id}. Please upload a CV first.")

        self.logger(f"CV loaded successfully for user {user_id}")
        return cv_content

    def scrape_jobs(
        self,
        min_salary: Optional[int] = 4000,
        employment_location: Optional[str] = "remote",
        posted_after: Optional[datetime] = None,
        timeout: int = 30,
    ) -> list[JobDict]:
        """Scrape jobs using the scrapper service.

        Automatically paginates through all pages until reaching the date cutoff.

        Args:
            min_salary: Minimum salary filter
            employment_location: Employment type or location filter
            posted_after: Only return jobs posted after this datetime (default: None, returns all jobs)
            timeout: Request timeout in seconds

        Returns:
            List of job dictionaries
        """
        self.logger("Scraping jobs...")
        jobs = self.scrapper_manager.scrape_jobs_as_dicts(
            min_salary=min_salary,
            employment_location=employment_location,
            posted_after=posted_after,
            timeout=timeout,
        )
        self.logger(f"Scraped {len(jobs)} jobs")
        return jobs

    def scrape_jobs_streaming(
        self,
        min_salary: Optional[int] = 4000,
        employment_location: Optional[str] = "remote",
        posted_after: Optional[datetime] = None,
        timeout: int = 30,
    ) -> Iterator[tuple[list[JobDict], int]]:
        """Scrape jobs using the scrapper service, yielding batches as they arrive.

        Automatically paginates through all pages until reaching the date cutoff,
        yielding each batch as soon as it's received from the scrapper.

        Args:
            min_salary: Minimum salary filter
            employment_location: Employment type or location filter
            posted_after: Only return jobs posted after this datetime (default: None, returns all jobs)
            timeout: Request timeout in seconds

        Yields:
            tuple[list[JobDict], int]: (batch_jobs, total_jobs_so_far)
        """
        self.logger("Starting streaming job scrape...")
        total_jobs = 0

        # Check if scrapper_manager has streaming method
        if hasattr(self.scrapper_manager, "scrape_jobs_streaming"):
            for batch_jobs in self.scrapper_manager.scrape_jobs_streaming(
                min_salary=min_salary,
                employment_location=employment_location,
                posted_after=posted_after,
                timeout=timeout,
            ):
                total_jobs += len(batch_jobs)
                self.logger(
                    f"Scraped batch: {len(batch_jobs)} jobs (total: {total_jobs})"
                )
                yield batch_jobs, total_jobs
        else:
            # Fallback to non-streaming if scrapper_manager doesn't support it
            self.logger("Scrapper manager doesn't support streaming, falling back to batch mode")
            jobs = self.scrapper_manager.scrape_jobs_as_dicts(
                min_salary=min_salary,
                employment_location=employment_location,
                posted_after=posted_after,
                timeout=timeout,
            )
            total_jobs = len(jobs)
            self.logger(f"Scraped {total_jobs} jobs")
            yield jobs, total_jobs

        self.logger(f"Completed scraping: {total_jobs} total jobs")

    def filter_jobs_list(self, jobs: Sequence[JobDict]) -> list[JobDict]:
        """Filter jobs based on configuration.

        Args:
            jobs: List of job dictionaries

        Returns:
            Filtered list of jobs
        """
        self.logger("Filtering jobs...")
        filtered_jobs = self.filter_service.filter(list(jobs))
        self.logger(f"Filtered jobs: {len(filtered_jobs)}/{len(jobs)} jobs passed")
        return filtered_jobs

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
        posted_after: Optional[datetime] = None,
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
            posted_after: Only return jobs posted after this datetime (default: None, returns all jobs)
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

        jobs = self.scrape_jobs(min_salary, employment_location, posted_after, timeout)

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
