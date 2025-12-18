from dataclasses import dataclass
from typing import Any, Callable, Optional, Protocol

from job_agent_backend.container import container
from job_agent_platform_contracts import IJobAgentOrchestrator, ICVRepository, IJobRepository


class OrchestratorFactory(Protocol):
    def __call__(
        self, *, logger: Optional[Callable[[str], None]] = None
    ) -> IJobAgentOrchestrator: ...


class CVRepositoryFactory(Protocol):
    def __call__(self, user_id: int) -> ICVRepository: ...


class JobRepositoryFactory(Protocol):
    def __call__(self) -> IJobRepository: ...


@dataclass(frozen=True)
class BotDependencies:
    orchestrator_factory: OrchestratorFactory
    cv_repository_factory: CVRepositoryFactory
    job_repository_factory: JobRepositoryFactory


def _create_cv_repository(user_id: int) -> ICVRepository:
    """Create a CV repository for a specific user."""
    orchestrator = container.orchestrator()
    cv_path = orchestrator.get_cv_path(user_id)
    cv_repository_class = container.cv_repository()
    return cv_repository_class(cv_path)


def _get_job_repository() -> IJobRepository:
    """Get a job repository instance."""
    return container.job_repository_factory()


def build_dependencies() -> BotDependencies:
    return BotDependencies(
        orchestrator_factory=container.orchestrator,
        cv_repository_factory=_create_cv_repository,
        job_repository_factory=_get_job_repository,
    )


def get_dependencies(context: Any) -> BotDependencies:
    return context.application.bot_data["dependencies"]
