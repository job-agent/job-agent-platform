"""Essay repository schemas."""

from job_agent_platform_contracts.essay_repository.schemas.essay_create import EssayCreate
from job_agent_platform_contracts.essay_repository.schemas.essay_update import EssayUpdate
from job_agent_platform_contracts.essay_repository.schemas.essay import Essay
from job_agent_platform_contracts.essay_repository.schemas.search_result import (
    EssaySearchResult,
)

__all__ = [
    "EssayCreate",
    "EssayUpdate",
    "Essay",
    "EssaySearchResult",
]
