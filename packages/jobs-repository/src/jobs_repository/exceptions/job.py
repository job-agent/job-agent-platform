"""Job-related exceptions."""

from jobs_repository.exceptions.base import JobRepositoryError


class JobNotFoundError(JobRepositoryError):
    """Raised when a job is not found."""

    def __init__(self, job_id: int | str, message: str | None = None):
        """Initialize exception."""
        self.job_id = job_id
        self.message = message or f"Job with id '{job_id}' not found"
        super().__init__(self.message)


class JobAlreadyExistsError(JobRepositoryError):
    """Raised when attempting to create a job that already exists."""

    def __init__(self, external_id: str, source: str, message: str | None = None):
        """Initialize exception."""
        self.external_id = external_id
        self.source = source
        self.message = (
            message or f"Job with external_id '{external_id}' from '{source}' already exists"
        )
        super().__init__(self.message)
