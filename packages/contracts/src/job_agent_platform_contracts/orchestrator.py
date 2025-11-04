"""Interface for job agent orchestration."""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


class IJobAgentOrchestrator(ABC):
    """Contract for orchestrating job processing workflows."""

    @abstractmethod
    def get_cv_path(self, user_id: int) -> Path:
        """Return the storage path for the CV associated with the user."""

    @abstractmethod
    def upload_cv(self, user_id: int, file_path: str) -> None:
        """Process and store a CV for the user from the provided file path."""

    @abstractmethod
    def has_cv(self, user_id: int) -> bool:
        """Determine whether the user has a stored CV."""

    @abstractmethod
    def load_cv(self, user_id: int) -> str:
        """Load the processed CV content for the user."""

    @abstractmethod
    def scrape_jobs(
        self,
        salary: int = 4000,
        employment: str = "remote",
        posted_after: Optional[datetime] = None,
        timeout: int = 30,
    ) -> List[Dict[str, Any]]:
        """Retrieve job listings matching the provided filters."""

    @abstractmethod
    def filter_jobs_list(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter job listings according to the configured rules."""

    @abstractmethod
    def process_job(
        self,
        job: Dict[str, Any],
        cv_content: str,
        db_session: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Execute processing workflows for a single job and return the results."""

    @abstractmethod
    def process_jobs_iterator(
        self,
        jobs: List[Dict[str, Any]],
        cv_content: str,
    ) -> Iterable[Tuple[int, int, Dict[str, Any]]]:
        """Yield processing results for each job alongside progress metadata."""

    @abstractmethod
    def run_complete_pipeline(
        self,
        user_id: int,
        salary: int = 4000,
        employment: str = "remote",
        posted_after: Optional[datetime] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Execute the end-to-end job processing workflow and return summary data."""
