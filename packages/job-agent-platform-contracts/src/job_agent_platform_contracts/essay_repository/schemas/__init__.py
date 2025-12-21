"""Essay repository schemas."""

from job_agent_platform_contracts.essay_repository.schemas.essay_create import EssayCreate
from job_agent_platform_contracts.essay_repository.schemas.essay_update import EssayUpdate
from job_agent_platform_contracts.essay_repository.schemas.essay import Essay

__all__ = [
    "EssayCreate",
    "EssayUpdate",
    "Essay",
]
