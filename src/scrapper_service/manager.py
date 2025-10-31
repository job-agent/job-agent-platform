"""
Scrapper Manager - Centralized service to handle all job scrappers

This module provides a unified interface that abstracts away multiple scrapper
implementations, presenting them as a single scraping service.
"""

from typing import List

from djinni_scrapper.scrapper import DjinniScrapper
from job_scrapper_contracts import JobScrapperInterface, Job, JobDict


class ScrapperManager(JobScrapperInterface):
    """
    Unified job scraping service that aggregates results from multiple sources.

    This class implements JobScrapperInterface and hides the complexity of managing
    multiple scrapper implementations. Users interact with a single, simple interface
    without needing to know about individual scrapper sources.

    Example:
        >>> from djinni_scrapper.scrapper import DjinniScrapper
        >>> manager = ScrapperManager()
        >>> manager.add_scrapper(DjinniScrapper)
        >>> jobs = manager.scrape_jobs(salary=5000)  # Aggregates from all sources
    """

    def __init__(self):
        """Initialize the scrapper manager with an empty scrapper registry."""
        self._scrappers: List[JobScrapperInterface] = [DjinniScrapper()]

    def scrape_jobs(
        self,
        salary: int = 4000,
        employment: str = "remote",
        page: int = 1,
        timeout: int = 30
    ) -> List[Job]:
        """
        Scrape jobs from all registered sources and return unified results.

        This method aggregates jobs from all scrapper implementations transparently,
        hiding the complexity of multiple data sources from the user.

        Args:
            salary: Minimum salary filter (default: 4000)
            employment: Employment type filter (default: "remote")
            page: Page number for pagination (default: 1)
            timeout: Request timeout in seconds (default: 30)

        Returns:
            Combined list of Job objects from all sources

        Raises:
            Exception: If any scrapper fails and no results can be returned

        Example:
            >>> manager = ScrapperManager()
            >>> manager.add_scrapper(DjinniScrapper)
            >>> jobs = manager.scrape_jobs(salary=5000)
            >>> print(f"Found {len(jobs)} jobs total")
        """
        all_jobs: List[Job] = []
        errors: List[str] = []

        for scrapper in self._scrappers:
            try:
                jobs = scrapper.scrape_jobs(
                    salary=salary,
                    employment=employment,
                    page=page,
                    timeout=timeout
                )
                all_jobs.extend(jobs)
            except Exception as e:
                errors.append(f"{scrapper.__class__.__name__}: {str(e)}")

        if not all_jobs and errors:
            raise Exception(f"All scrappers failed: {'; '.join(errors)}")

        return all_jobs

    def scrape_jobs_as_dicts(
        self,
        salary: int = 4000,
        employment: str = "remote",
        page: int = 1,
        timeout: int = 30
    ) -> List[JobDict]:
        """
        Scrape jobs from all sources and return as dictionaries.

        This method aggregates jobs from all scrapper implementations and returns
        them as dictionaries, useful for JSON serialization or API responses.

        Args:
            salary: Minimum salary filter (default: 4000)
            employment: Employment type filter (default: "remote")
            page: Page number for pagination (default: 1)
            timeout: Request timeout in seconds (default: 30)

        Returns:
            Combined list of job dictionaries from all sources

        Example:
            >>> jobs = manager.scrape_jobs_as_dicts(salary=5000)
        """
        jobs = self.scrape_jobs(
            salary=salary,
            employment=employment,
            page=page,
            timeout=timeout
        )
        return [job.to_dict() for job in jobs]