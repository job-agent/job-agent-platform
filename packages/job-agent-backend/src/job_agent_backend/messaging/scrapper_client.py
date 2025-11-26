"""RabbitMQ-based scrapper client implementing ScrapperManagerProtocol."""

import logging
from datetime import datetime
from typing import Callable, Iterator, Optional

from job_scrapper_contracts import JobDict
from job_agent_platform_contracts import IJobRepository

from job_agent_backend.messaging.producer import ScrapperProducer


class ScrapperClient:
    """RabbitMQ-based client for scrapping jobs.

    Implements the same interface as ScrapperManager but uses RabbitMQ
    message broker for communication with scrapper-service.
    """

    def __init__(
        self,
        rabbitmq_url: Optional[str] = None,
        job_repository_factory: Optional[Callable[[], IJobRepository]] = None,
        source: str = "djinni",
        url_lookback_days: int = 60,
    ):
        """Initialize the scrapper client.

        Args:
            rabbitmq_url: RabbitMQ connection URL
            job_repository_factory: Factory for creating job repository instances (for querying existing URLs)
            source: Job source identifier (default: "djinni")
            url_lookback_days: Number of days to look back for existing URLs (default: 60)
                              Only URLs from jobs posted within this window will be filtered.
                              Recommended: 60 days for daily scraping, 90+ for weekly scraping.
        """
        self.producer = ScrapperProducer(rabbitmq_url)
        self.job_repository_factory = job_repository_factory
        self.source = source
        self.url_lookback_days = url_lookback_days
        self.logger = logging.getLogger(__name__)

    def _get_existing_urls(self) -> Optional[list[str]]:
        """Query existing URLs from the job repository with time-window filtering.

        Returns:
            List of existing URLs from the last N days, or None if repository not configured
        """
        if not self.job_repository_factory:
            return None

        try:
            job_repository = self.job_repository_factory()
            existing_urls = job_repository.get_existing_urls_by_source(
                self.source, days=self.url_lookback_days
            )
            self.logger.info(
                f"Found {len(existing_urls)} existing URLs for source '{self.source}' "
                f"(last {self.url_lookback_days} days)"
            )
            return existing_urls
        except Exception as e:
            self.logger.warning(f"Failed to query existing URLs: {e}")
            return None

    def scrape_jobs_streaming(
        self,
        min_salary: Optional[int] = 4000,
        employment_location: Optional[str] = "remote",
        posted_after: Optional[datetime] = None,
        timeout: int = 30,
    ) -> Iterator[list[JobDict]]:
        """Scrape jobs via RabbitMQ, yielding batches as they arrive.

        This method yields each batch of jobs as soon as it's received from the scrapper,
        allowing for incremental processing instead of waiting for all pages.

        Args:
            min_salary: Minimum salary requirement
            employment_location: Employment type or location (e.g., "remote", "on-site")
            posted_after: Only include jobs posted after this date
            timeout: Request timeout in seconds

        Yields:
            list[JobDict]: Batch of jobs for each batch

        Raises:
            TimeoutError: If no response is received
            Exception: If scraping fails
        """
        # Convert datetime to ISO format string
        posted_after_str = posted_after.isoformat() if posted_after else None

        # Get existing URLs to filter them out during scraping
        existing_urls = self._get_existing_urls()

        self.logger.info(
            f"Sending streaming scrape request: min_salary={min_salary}, employment_location={employment_location}, "
            f"posted_after={posted_after_str}, timeout={timeout}, existing_urls_count={len(existing_urls) if existing_urls else 0}"
        )

        # Stream batches via RabbitMQ
        for response in self.producer.scrape_jobs_streaming(
            min_salary=min_salary,
            employment_location=employment_location,
            posted_after=posted_after_str,
            existing_urls=existing_urls,
            timeout=timeout,
        ):
            jobs = response.get("jobs", [])
            jobs_count = len(jobs)

            self.logger.info(f"Yielding batch: {jobs_count} jobs")

            yield jobs
