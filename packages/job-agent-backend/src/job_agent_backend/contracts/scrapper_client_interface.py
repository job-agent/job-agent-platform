"""Scrapper client interface definitions."""

from datetime import datetime
from typing import Iterator, Optional, Protocol

from job_scrapper_contracts import JobDict


class IScrapperClient(Protocol):
    """Interface for components that provide job scraping capabilities."""

    def scrape_jobs_streaming(
        self,
        min_salary: Optional[int] = 4000,
        employment_location: Optional[str] = "remote",
        posted_after: Optional[datetime] = None,
        timeout: int = 30,
    ) -> Iterator[list[JobDict]]:
        """Scrape jobs, yielding batches as they arrive.

        Args:
            min_salary: Minimum salary requirement
            employment_location: Employment type or location
            posted_after: Only include jobs posted after this date
            timeout: Request timeout in seconds

        Yields:
            list[JobDict]: Batch of jobs for each batch

        Raises:
            TimeoutError: If no response is received
            Exception: If scraping fails
        """
        ...
