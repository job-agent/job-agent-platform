"""Repository pattern implementation for CV operations.

This repository provides methods for managing a single CV stored in a file.
"""

from typing import Optional
from pathlib import Path

from job_agent_platform_contracts import ICVRepository


class CVRepository(ICVRepository):
    """
    Repository for managing CV operations.

    This repository manages a single CV stored as a string in a file.
    Provides operations for creating, retrieving, and updating the CV.
    """

    def __init__(self, file_path: str | Path):
        """
        Initialize the repository.

        Args:
            file_path: Path to the file where CV will be stored
        """
        self.file_path = Path(file_path)

    def create(self, cv_data: str) -> str:
        """
        Create or overwrite the CV file.

        Args:
            cv_data: CV data as string

        Returns:
            The created CV data

        Raises:
            IOError: If file cannot be written
        """
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(cv_data, encoding="utf-8")
        return cv_data

    def find(self) -> Optional[str]:
        """
        Find and return the CV data from file.

        Returns:
            CV data as string if file exists, None otherwise
        """
        if not self.file_path.exists():
            return None
        return self.file_path.read_text(encoding="utf-8")

    def update(self, cv_data: str) -> str:
        """
        Update the CV by rewriting the file.

        Args:
            cv_data: Updated CV data as string

        Returns:
            The updated CV data

        Raises:
            IOError: If file cannot be written
        """
        self.file_path.write_text(cv_data, encoding="utf-8")
        return cv_data
