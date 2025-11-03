"""Core orchestration logic for job processing.

This module contains the business logic for scraping, filtering, and processing jobs.
It can be used by any interface (CLI, Telegram, Web, etc.).
"""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

from scrapper_service import ScrapperManager
from jobs_repository import init_db
from jobs_repository.database.session import get_db_session
from cvs_repository import CVRepository

from job_agent_backend.filter_service import FilterConfig, filter_jobs
from job_agent_backend.workflows import run_job_processing, run_pii_removal
from job_agent_backend.utils import load_cv_from_pdf, load_cv_from_text


class JobAgentOrchestrator:
    """Orchestrates the complete job processing pipeline.

    This class provides a clean interface for running the job agent workflow
    from any entry point (CLI, Telegram bot, API, etc.).
    """

    def __init__(self, logger: Optional[Callable[[str], None]] = None):
        """Initialize the orchestrator.

        Args:
            logger: Optional logging function to report progress.
                   If None, will use print().
        """
        self.logger = logger or print
        self.scrapper_manager = ScrapperManager()
        self.cv_content: Optional[str] = None
        self.cleaned_cv: Optional[str] = None

    def _get_cv_path(self, user_id: int) -> Path:
        """Get the storage path for a user's CV.

        Args:
            user_id: User identifier (e.g., Telegram user ID)

        Returns:
            Path object for the user's CV file
        """
        # Store CVs in data/cvs/ directory relative to package root
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

        # Determine file type and extract content
        if file_path_lower.endswith(".pdf"):
            self.logger(f"Processing PDF CV for user {user_id}")
            cv_content = load_cv_from_pdf(file_path)
        elif file_path_lower.endswith(".txt"):
            self.logger(f"Processing text CV for user {user_id}")
            cv_content = load_cv_from_text(file_path)
        else:
            # Unsupported file format
            extension = Path(file_path).suffix
            raise ValueError(
                f"Unsupported file format: {extension}. " f"Supported formats: .pdf, .txt"
            )

        if not cv_content:
            raise ValueError("Failed to extract content from CV file")

        # Save the CV content
        cv_path = self.get_cv_path(user_id)
        cv_repository = CVRepository(cv_path)
        cv_repository.create(cv_content)
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
            cv_repository = CVRepository(cv_path)
            return cv_repository.find() is not None
        except Exception:
            return False

    def _get_filter_config(self) -> FilterConfig:
        """Build filter configuration from environment variables.

        Returns:
            FilterConfig dictionary with filtering parameters
        """
        filter_config: FilterConfig = {}

        if os.getenv("FILTER_MAX_MONTHS_OF_EXPERIENCE"):
            filter_config["max_months_of_experience"] = int(
                os.getenv("FILTER_MAX_MONTHS_OF_EXPERIENCE")
            )

        if os.getenv("FILTER_LOCATION_ALLOWS_TO_APPLY"):
            filter_config["location_allows_to_apply"] = os.getenv(
                "FILTER_LOCATION_ALLOWS_TO_APPLY"
            ).lower() in ("true", "1", "yes")

        return filter_config

    def scrape_jobs(
        self,
        salary: int = 4000,
        employment: str = "remote",
        posted_after: Optional[datetime] = None,
        timeout: int = 30,
    ) -> List[Dict[str, Any]]:
        """Scrape jobs using the scrapper service.

        Automatically paginates through all pages until reaching the date cutoff.

        Args:
            salary: Minimum salary filter
            employment: Employment type filter
            posted_after: Only return jobs posted after this datetime (default: None, returns all jobs)
            timeout: Request timeout in seconds

        Returns:
            List of job dictionaries
        """
        self.logger("Scraping jobs...")
        jobs = self.scrapper_manager.scrape_jobs_as_dicts(
            salary=salary, employment=employment, posted_after=posted_after, timeout=timeout
        )
        self.logger(f"Scraped {len(jobs)} jobs")
        return jobs

    def filter_jobs_list(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter jobs based on configuration.

        Args:
            jobs: List of job dictionaries

        Returns:
            Filtered list of jobs
        """
        self.logger("Filtering jobs...")
        filter_config = self._get_filter_config()
        filtered_jobs = filter_jobs(jobs, filter_config)
        self.logger(f"Filtered jobs: {len(filtered_jobs)}/{len(jobs)} jobs passed")
        return filtered_jobs

    def load_and_clean_cv(
        self, cv_path: Optional[str] = None, user_id: Optional[int] = None
    ) -> str:
        """Load CV from file and remove PII.

        Args:
            cv_path: Optional path to CV file (PDF or text). If not provided and user_id
                    is given, will use user-specific CV path. If neither is provided,
                    uses default PDF path. If the path ends with .txt, loads as text file.
                    Otherwise loads as PDF.
            user_id: Optional user identifier. If provided and cv_path is not, will load
                    the user's CV from the standard location.

        Returns:
            Cleaned CV content

        Raises:
            ValueError: If CV cannot be loaded
        """
        if self.cleaned_cv:
            return self.cleaned_cv

        self.logger("Loading CV...")

        # Determine CV path if not provided
        if cv_path is None and user_id is not None:
            cv_path = str(self.get_cv_path(user_id))

        # Determine if we're loading from text or PDF
        if cv_path and cv_path.endswith(".txt"):
            self.cv_content = load_cv_from_text(cv_path)
        else:
            self.cv_content = load_cv_from_pdf(cv_path)

        if not self.cv_content:
            raise ValueError("Failed to load CV content")
        self.logger("CV loaded successfully")

        self.logger("Removing PII from CV...")
        self.cleaned_cv = run_pii_removal(self.cv_content)
        self.logger("PII removed from CV")

        return self.cleaned_cv

    def process_job(self, job: Dict[str, Any], cv_content: str, db_session=None) -> Dict[str, Any]:
        """Process a single job with the workflows system.

        Args:
            job: Job dictionary to process
            cv_content: Cleaned CV content
            db_session: Optional database session for storing jobs

        Returns:
            Dictionary containing processing results:
            - is_relevant: Whether the job is relevant to the candidate
            - extracted_must_have_skills: List of must-have skills (for relevant jobs)
            - extracted_nice_to_have_skills: List of nice-to-have skills (for relevant jobs)
            - status: Final workflow status
            - job: Original job dictionary
        """
        result = run_job_processing(job, cv_content, db_session)
        return result

    def run_complete_pipeline(
        self,
        salary: int = 4000,
        employment: str = "remote",
        posted_after: Optional[datetime] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Run the complete job processing pipeline.

        This is the main entry point that:
        1. Initializes database (creates tables if needed)
        2. Scrapes jobs (automatically paginates until date cutoff)
        3. Filters unsuitable jobs
        4. Loads and cleans CV
        5. Processes each job with workflows and stores relevant ones

        Args:
            salary: Minimum salary filter
            employment: Employment type filter
            posted_after: Only return jobs posted after this datetime (default: None, returns all jobs)
            timeout: Request timeout in seconds

        Returns:
            Dictionary with pipeline results and statistics
        """
        # Step 0: Initialize database (create tables if they don't exist)
        self.logger("Initializing database...")
        try:
            init_db()
            self.logger("Database initialized successfully")
        except Exception as e:
            self.logger(f"Warning: Database initialization failed: {e}")
            self.logger("Continuing without database storage...")

        # Step 1: Scrape jobs
        jobs = self.scrape_jobs(salary, employment, posted_after, timeout)

        # Step 2: Filter jobs
        filtered_jobs = self.filter_jobs_list(jobs)

        # Step 3: Load and clean CV
        cleaned_cv = self.load_and_clean_cv()

        # Step 4: Process jobs with database session
        self.logger(f"Processing {len(filtered_jobs)} jobs with workflows system...")

        # Create a database session for all jobs
        db_gen = get_db_session()
        db_session = next(db_gen)

        try:
            for idx, job in enumerate(filtered_jobs, 1):
                self.logger(f"\nProcessing job {idx}/{len(filtered_jobs)}")
                self.process_job(job, cleaned_cv, db_session)

            results = {
                "total_scraped": len(jobs),
                "total_filtered": len(filtered_jobs),
                "total_processed": len(filtered_jobs),
            }

            self.logger(f"\nPipeline completed - Processed {len(filtered_jobs)} jobs")
            return results
        finally:
            # Close the database session
            db_session.close()
