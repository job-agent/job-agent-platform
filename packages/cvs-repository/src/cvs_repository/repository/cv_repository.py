"""Repository pattern implementation for CV operations.

This repository provides methods for managing a single CV stored in a file.
"""

from typing import Optional
from pathlib import Path

from job_agent_platform_contracts import ICVRepository


class CVRepository(ICVRepository):
    """Repository for managing a single CV stored as a string in a file."""

    def __init__(self, file_path: str | Path):
        """Initialize the repository with the given file path."""
        self.file_path = Path(file_path)

    def create(self, cv_data: str) -> str:
        """Create or overwrite the CV file, creating parent directories if needed."""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise IOError(
                f"Failed to create directory for CV file at {self.file_path.parent}: {e}"
            ) from e

        try:
            self.file_path.write_text(cv_data, encoding="utf-8")
        except OSError as e:
            raise IOError(f"Failed to write CV file at {self.file_path}: {e}") from e

        return cv_data

    def find(self) -> Optional[str]:
        """Return the CV data from file, or None if file does not exist."""
        if not self.file_path.exists():
            return None

        try:
            return self.file_path.read_text(encoding="utf-8")
        except OSError as e:
            raise IOError(f"Failed to read CV file at {self.file_path}: {e}") from e

    def update(self, cv_data: str) -> str:
        """Update the CV by rewriting the file; raises FileNotFoundError if file does not exist."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Cannot update CV: file does not exist at {self.file_path}")

        try:
            self.file_path.write_text(cv_data, encoding="utf-8")
        except OSError as e:
            raise IOError(f"Failed to update CV file at {self.file_path}: {e}") from e

        return cv_data
