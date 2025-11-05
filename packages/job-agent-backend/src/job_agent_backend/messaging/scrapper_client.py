"""RabbitMQ-based scrapper client implementing ScrapperManagerProtocol."""

import logging
from datetime import datetime
from typing import Optional

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
        salary: int = 4000,
        employment: str = "remote",
        posted_after: Optional[datetime] = None,
        timeout: int = 30,
    ) -> list[JobDict]:
        """Scrape jobs via RabbitMQ message broker.

        Args:
            salary: Minimum salary requirement
            employment: Employment type (e.g., "remote", "full-time")
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
            f"Sending scrape request: salary={salary}, employment={employment}, "
            f"posted_after={posted_after_str}, timeout={timeout}"
        )

        # Send request via RabbitMQ
        response = self.producer.send_scrape_request(
            salary=salary,
            employment=employment,
            posted_after=posted_after_str,
            timeout=timeout,
        )

        self.logger.info(f"Received {response['jobs_count']} jobs from scrapper")

        return response["jobs"]
