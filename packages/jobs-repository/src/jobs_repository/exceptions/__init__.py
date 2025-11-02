"""Exceptions module - custom exceptions."""

from jobs_repository.exceptions.base import JobRepositoryError
from jobs_repository.exceptions.job import JobNotFoundError, JobAlreadyExistsError
from jobs_repository.exceptions.database import (
    DatabaseConnectionError,
    TransactionError,
)
from jobs_repository.exceptions.validation import ValidationError

__all__ = [
    "JobRepositoryError",
    "JobNotFoundError",
    "JobAlreadyExistsError",
    "DatabaseConnectionError",
    "TransactionError",
    "ValidationError",
]
