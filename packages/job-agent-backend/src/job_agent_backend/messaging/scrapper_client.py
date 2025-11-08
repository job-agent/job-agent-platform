"""RabbitMQ-based scrapper client implementing ScrapperManagerProtocol."""

import logging
from datetime import datetime
from typing import Iterator, Optional

from job_scrapper_contracts import JobDict

from job_agent_backend.messaging.producer import ScrapperProducer


class ScrapperClient:
    """RabbitMQ-based client for scrapping jobs.

    Implements the same interface as ScrapperManager but uses RabbitMQ
    message broker for communication with scrapper-service.
    """

    def __init__(self, rabbitmq_url: Optional[str] = None):
        """Initialize the scrapper client.

        Args:
            rabbitmq_url: RabbitMQ connection URL
        """
        self.producer = ScrapperProducer(rabbitmq_url)
        self.logger = logging.getLogger(__name__)

    def scrape_jobs_as_dicts(
        self,
        min_salary: Optional[int] = 4000,
        employment_location: Optional[str] = "remote",
        posted_after: Optional[datetime] = None,
        timeout: int = 30,
    ) -> list[JobDict]:
        """Scrape jobs via RabbitMQ message broker.

        Args:
            min_salary: Minimum salary requirement
            employment_location: Employment type or location (e.g., "remote", "on-site")
            posted_after: Only include jobs posted after this date
            timeout: Request timeout in seconds

        Returns:
            list[JobDict]: List of scraped jobs

        Raises:
            TimeoutError: If no response is received
            Exception: If scraping fails
        """
        # Convert datetime to ISO format string
        posted_after_str = posted_after.isoformat() if posted_after else None

        self.logger.info(
            f"Sending scrape request: min_salary={min_salary}, employment_location={employment_location}, "
            f"posted_after={posted_after_str}, timeout={timeout}"
        )

        # Send request via RabbitMQ
        response = self.producer.send_scrape_request(
            min_salary=min_salary,
            employment_location=employment_location,
            posted_after=posted_after_str,
            timeout=timeout,
        )

        self.logger.info(f"Received {response['jobs_count']} jobs from scrapper")

        return response["jobs"]

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

        self.logger.info(
            f"Sending streaming scrape request: min_salary={min_salary}, employment_location={employment_location}, "
            f"posted_after={posted_after_str}, timeout={timeout}"
        )

        # Stream batches via RabbitMQ
        for response in self.producer.scrape_jobs_streaming(
            min_salary=min_salary,
            employment_location=employment_location,
            posted_after=posted_after_str,
            timeout=timeout,
        ):
            jobs = response.get("jobs", [])
            jobs_count = len(jobs)

            self.logger.info(f"Yielding batch: {jobs_count} jobs")

            yield jobs
