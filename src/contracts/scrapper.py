"""Scrapper service interface definition.

This module defines the interface for job scrapping services, ensuring that
consumers depend on abstractions rather than concrete implementations.
"""

from abc import ABC, abstractmethod
from typing import List

from job_scrapper_contracts import Job, JobDict


class ScrapperServiceInterface(ABC):
    """
    Interface for job scrapping services.

    This interface defines the contract that all scrapper service implementations
    must follow. It allows for dependency inversion where high-level modules
    (like agents or connectors) depend on this abstraction rather than concrete
    scrapper implementations.

    Example:
        >>> class MyScrapperService(ScrapperServiceInterface):
        ...     def scrape_jobs(self, salary=4000, employment="remote", page=1, timeout=30):
        ...         # implementation
        ...         pass
    """

    @abstractmethod
    def scrape_jobs(
        self,
        salary: int = 4000,
        employment: str = "remote",
        page: int = 1,
        timeout: int = 30
    ) -> List[Job]:
        """
        Scrape jobs from configured sources.

        Args:
            salary: Minimum salary filter (default: 4000)
            employment: Employment type filter (default: "remote")
            page: Page number for pagination (default: 1)
            timeout: Request timeout in seconds (default: 30)

        Returns:
            List of Job objects matching the criteria

        Raises:
            Exception: If scraping fails and no results can be returned
        """
        pass

    @abstractmethod
    def scrape_jobs_as_dicts(
        self,
        salary: int = 4000,
        employment: str = "remote",
        page: int = 1,
        timeout: int = 30
    ) -> List[JobDict]:
        """
        Scrape jobs from configured sources and return as dictionaries.

        Args:
            salary: Minimum salary filter (default: 4000)
            employment: Employment type filter (default: "remote")
            page: Page number for pagination (default: 1)
            timeout: Request timeout in seconds (default: 30)

        Returns:
            List of job dictionaries matching the criteria
        """
        pass
