"""Filter service contract definitions."""

from abc import ABC, abstractmethod
from typing import List, Mapping, Optional, Any

from job_scrapper_contracts import JobDict


class IFilterService(ABC):
    """Interface for services that filter job posts."""

    @abstractmethod
    def configure(self, config: Optional[Mapping[str, Any]]) -> None: ...

    @abstractmethod
    def filter(self, jobs: List[JobDict]) -> List[JobDict]: ...
