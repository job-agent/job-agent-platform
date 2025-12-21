"""Job filter service for filtering unsuitable job posts.

This module provides filtering capabilities for job posts coming from the
scrapper service before they are passed to the workflows system.
"""

from typing import Callable, List, Optional, Tuple

from job_scrapper_contracts import JobDict
from job_agent_platform_contracts import IJobRepository

from .filter_config import FilterConfig
from ..contracts import IFilterService


class FilterService(IFilterService):
    """
    Service for filtering job posts based on optional configuration.

    Args:
        config: Optional configuration for filtering criteria. When omitted,
            a default policy limits experience and requires applications to be allowed.
    """

    def __init__(
        self,
        config: Optional[FilterConfig] = None,
        job_repository_factory: Optional[Callable[[], IJobRepository]] = None,
    ) -> None:
        self.config: FilterConfig = config or {
            "max_months_of_experience": 60,
            "location_allows_to_apply": True,
        }
        self._job_repository_factory = job_repository_factory

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

        filtered_jobs: List[JobDict] = []
        repository = self._resolve_repository()

        for job in jobs:
            if not self._passes_experience(job):
                continue

            if not self._passes_location(job):
                continue

            if repository and self._is_existing_job(repository, job):
                continue

            filtered_jobs.append(job)

        return filtered_jobs

    def filter_with_rejected(self, jobs: List[JobDict]) -> Tuple[List[JobDict], List[JobDict]]:
        """
        Filter jobs and return both passed and rejected lists.

        Args:
            jobs: List of job dictionaries to filter

        Returns:
            Tuple of (passed_jobs, rejected_jobs) where:
            - passed_jobs: Jobs that passed all filter criteria
            - rejected_jobs: Jobs that failed at least one filter criterion
              (excluding jobs that already exist in the repository)
        """
        passed_jobs: List[JobDict] = []
        rejected_jobs: List[JobDict] = []
        repository = self._resolve_repository()

        for job in jobs:
            # Skip jobs that already exist in the repository
            if repository and self._is_existing_job(repository, job):
                continue

            # Check filter criteria
            if not self._passes_experience(job) or not self._passes_location(job):
                rejected_jobs.append(job)
                continue

            passed_jobs.append(job)

        return passed_jobs, rejected_jobs

    def _resolve_repository(self) -> Optional[IJobRepository]:
        if self._job_repository_factory is None:
            return None

        return self._job_repository_factory()

    def _is_existing_job(self, repository: IJobRepository, job: JobDict) -> bool:
        external_id = self._extract_external_id(job)
        source = job.get("source")

        if external_id and repository.get_by_external_id(external_id, source):
            return True

        title = job.get("title")
        company_name = self._extract_company_name(job)

        if not title or not company_name:
            return False

        return repository.has_active_job_with_title_and_company(title, company_name)

    def _extract_external_id(self, job: JobDict) -> Optional[str]:
        job_id = job.get("job_id")
        if job_id is not None:
            return str(job_id)

        external_id = job.get("external_id")
        if external_id is not None:
            return str(external_id)

        return None

    def _extract_company_name(self, job: JobDict) -> Optional[str]:
        company = job.get("company")
        if isinstance(company, dict):
            name = company.get("name")
            if name:
                return str(name)

        company_name = job.get("company_name")
        if company_name:
            return str(company_name)

        return None

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
