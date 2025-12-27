"""Exception classes for essay repository operations."""

from job_agent_platform_contracts.job_repository.exceptions import (
    RepositoryError,
)


class EssayRepositoryError(RepositoryError):
    """Base exception for essay repository-specific errors."""

    pass


class EssayNotFoundError(EssayRepositoryError):
    """Raised when a requested essay cannot be found."""

    def __init__(self, essay_id: int):
        self.essay_id = essay_id
        super().__init__(f"Essay with id '{essay_id}' not found")


class EssayValidationError(EssayRepositoryError):
    """Raised when essay data validation fails."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation error on field '{field}': {message}")
