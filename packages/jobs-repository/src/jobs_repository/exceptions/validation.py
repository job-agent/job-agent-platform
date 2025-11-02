"""Validation exceptions."""

from jobs_repository.exceptions.base import JobRepositoryError


class ValidationError(JobRepositoryError):
    """Raised when job data validation fails."""

    def __init__(self, field: str, message: str):
        """Initialize exception."""
        self.field = field
        self.message = f"Validation error for field '{field}': {message}"
        super().__init__(self.message)
