"""Core orchestration logic for job processing.

This module contains the business logic for scraping, filtering, and processing jobs.
It can be used by any interface (CLI, Telegram, Web, etc.).
"""

import os
from typing import List, Dict, Any, Optional, Callable

from dotenv import load_dotenv
from scrapper_service import ScrapperManager

from job_agent_backend.filter_service import FilterConfig, filter_jobs
from job_agent_backend.workflows import run_job_processing, run_pii_removal
from job_agent_backend.utils import load_cv_from_pdf

# Load environment variables from .env file
load_dotenv()


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
        page: int = 1,
        timeout: int = 30
    ) -> List[Dict[str, Any]]:
        """Scrape jobs using the scrapper service.

        Args:
            salary: Minimum salary filter
            employment: Employment type filter
            page: Page number for pagination
            timeout: Request timeout in seconds

        Returns:
            List of job dictionaries
        """
        self.logger("Scraping jobs...")
        jobs = self.scrapper_manager.scrape_jobs_as_dicts(
            salary=salary,
            employment=employment,
            page=page,
            timeout=timeout
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

    def load_and_clean_cv(self) -> str:
        """Load CV from PDF and remove PII.

        Returns:
            Cleaned CV content

        Raises:
            ValueError: If CV cannot be loaded
        """
        if self.cleaned_cv:
            return self.cleaned_cv

        self.logger("Loading CV...")
        self.cv_content = load_cv_from_pdf()
        if not self.cv_content:
            raise ValueError("Failed to load CV content")
        self.logger("CV loaded successfully")

        self.logger("Removing PII from CV...")
        self.cleaned_cv = run_pii_removal(self.cv_content)
        self.logger("PII removed from CV")

        return self.cleaned_cv

    def process_job(self, job: Dict[str, Any], cv_content: str) -> None:
        """Process a single job with the workflows system.

        Args:
            job: Job dictionary to process
            cv_content: Cleaned CV content
        """
        run_job_processing(job, cv_content)

    def run_complete_pipeline(
        self,
        salary: int = 4000,
        employment: str = "remote",
        page: int = 1,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Run the complete job processing pipeline.

        This is the main entry point that:
        1. Scrapes jobs
        2. Filters unsuitable jobs
        3. Loads and cleans CV
        4. Processes each job with workflows

        Args:
            salary: Minimum salary filter
            employment: Employment type filter
            page: Page number for pagination
            timeout: Request timeout in seconds

        Returns:
            Dictionary with pipeline results and statistics
        """
        # Step 1: Scrape jobs
        jobs = self.scrape_jobs(salary, employment, page, timeout)

        # Step 2: Filter jobs
        filtered_jobs = self.filter_jobs_list(jobs)

        # Step 3: Load and clean CV
        cleaned_cv = self.load_and_clean_cv()

        # Step 4: Process jobs
        self.logger(f"Processing {len(filtered_jobs)} jobs with workflows system...")

        for idx, job in enumerate(filtered_jobs, 1):
            self.logger(f"\nProcessing job {idx}/{len(filtered_jobs)}")
            self.process_job(job, cleaned_cv)

        results = {
            "total_scraped": len(jobs),
            "total_filtered": len(filtered_jobs),
            "total_processed": len(filtered_jobs)
        }

        self.logger(f"\nPipeline completed - Processed {len(filtered_jobs)} jobs")
        return results
