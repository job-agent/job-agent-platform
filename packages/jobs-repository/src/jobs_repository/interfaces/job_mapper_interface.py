"""Interface for job mapping service."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from job_scrapper_contracts import JobDict

if TYPE_CHECKING:
    from jobs_repository.models import Job
    from jobs_repository.types import JobModelDict, JobSerializedDict


class IJobMapper(ABC):
    """Interface for bidirectional mapping between Job model and contract data."""

    @abstractmethod
    def map_to_model(self, job_data: JobDict) -> JobModelDict:
        """Transform JobDict contract data to Job model field dictionary."""

    @abstractmethod
    def map_from_model(self, job: Job) -> JobSerializedDict:
        """Transform Job model to dictionary representation."""
