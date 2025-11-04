"""Exception classes for job repository operations."""


class JobAgentError(Exception):
    """Base exception for all job-agent platform errors."""

    pass


class RepositoryError(JobAgentError):
    """Base exception for repository-related errors."""

    pass


class JobRepositoryError(RepositoryError):
    """Base exception for job repository-specific errors."""

    pass


class JobAlreadyExistsError(JobRepositoryError):
    """Raised when attempting to create a job that already exists."""

    def __init__(self, external_id: str, source: str):
        self.external_id = external_id
        self.source = source
        super().__init__(
            f"Job with external_id '{external_id}' from source '{source}' already exists"
        )


class JobNotFoundError(JobRepositoryError):
    """Raised when a requested job cannot be found."""

    def __init__(self, identifier: str | int, identifier_type: str = "id"):
        self.identifier = identifier
        self.identifier_type = identifier_type
        super().__init__(f"Job with {identifier_type} '{identifier}' not found")


class ValidationError(JobRepositoryError):
    """Raised when data validation fails."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation error on field '{field}': {message}")
