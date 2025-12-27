"""Filter service interface definitions."""

from typing import Any, List, Mapping, Optional, Protocol, Tuple

from job_scrapper_contracts import JobDict


class IFilterService(Protocol):
    """Interface for services that filter job posts."""

    def configure(self, config: Optional[Mapping[str, Any]]) -> None: ...

    def filter(self, jobs: List[JobDict]) -> List[JobDict]: ...

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
        ...
