"""Filter service interface definitions."""

from abc import ABC, abstractmethod
from typing import List, Mapping, Optional, Any, Tuple

from job_scrapper_contracts import JobDict


class IFilterService(ABC):
    """Interface for services that filter job posts."""

    @abstractmethod
    def configure(self, config: Optional[Mapping[str, Any]]) -> None: ...

    @abstractmethod
    def filter(self, jobs: List[JobDict]) -> List[JobDict]: ...

    @abstractmethod
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
