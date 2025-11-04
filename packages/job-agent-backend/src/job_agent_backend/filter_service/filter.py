"""Job filter service for filtering unsuitable job posts.

This module provides filtering capabilities for job posts coming from the
scrapper service before they are passed to the workflows system.
"""

from typing import List, Optional

from job_scrapper_contracts import JobDict
from job_agent_backend.contracts.filter_service import IFilterService

from .filter_config import FilterConfig


class FilterService(IFilterService):
    """
    Service for filtering unsuitable job posts based on configuration criteria.

    Args:
        config: Optional configuration for filtering criteria.
    """

    def __init__(self, config: Optional[FilterConfig] = None) -> None:
        self.config: FilterConfig = config or {}

    def configure(self, config: Optional[FilterConfig]) -> None:
        self.config = config or {}

    def filter(self, jobs: List[JobDict]) -> List[JobDict]:
        """
        Filter unsuitable job posts based on the configured criteria.

        Args:
            jobs: List of job dictionaries from the scrapper service.

        Returns:
            Filtered list of job dictionaries.
        """

        if not self.config:
            return jobs

        filtered_jobs: List[JobDict] = []

        for job in jobs:
            if not self._passes_experience(job):
                continue

            if not self._passes_location(job):
                continue

            filtered_jobs.append(job)

        return filtered_jobs

    def _passes_experience(self, job: JobDict) -> bool:
        if "max_months_of_experience" not in self.config:
            return True

        experience_months = job.get("experience_months", 0)

        return experience_months <= self.config["max_months_of_experience"]

    def _passes_location(self, job: JobDict) -> bool:
        if not self.config.get("location_allows_to_apply"):
            return True

        location = job.get("location", {})
        can_apply = location.get("can_apply", False)

        return can_apply
