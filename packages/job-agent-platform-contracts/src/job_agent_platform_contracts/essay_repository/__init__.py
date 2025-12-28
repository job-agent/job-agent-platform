"""Essay repository contracts and exceptions."""

from job_agent_platform_contracts.essay_repository.repository import IEssayRepository
from job_agent_platform_contracts.essay_repository.schemas import (
    EssayCreate,
    EssayUpdate,
    Essay,
    EssaySearchResult,
)
from job_agent_platform_contracts.essay_repository.exceptions import (
    EssayRepositoryError,
    EssayNotFoundError,
    EssayValidationError,
)

__all__ = [
    "IEssayRepository",
    "EssayCreate",
    "EssayUpdate",
    "Essay",
    "EssaySearchResult",
    "EssayRepositoryError",
    "EssayNotFoundError",
    "EssayValidationError",
]
