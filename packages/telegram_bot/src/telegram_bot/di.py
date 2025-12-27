from dataclasses import dataclass
from typing import Any, Callable, Optional, Protocol

from job_agent_backend.container import container
from job_agent_backend.contracts import IEssaySearchService
from job_agent_platform_contracts import IJobAgentOrchestrator, ICVRepository


class OrchestratorFactory(Protocol):
    def __call__(
        self, *, logger: Optional[Callable[[str], None]] = None
    ) -> IJobAgentOrchestrator: ...


class CVRepositoryFactory(Protocol):
    def __call__(self, user_id: int) -> ICVRepository: ...


class EssayServiceFactory(Protocol):
    def __call__(self) -> IEssaySearchService: ...


@dataclass(frozen=True)
class BotDependencies:
    orchestrator_factory: OrchestratorFactory
    cv_repository_factory: CVRepositoryFactory
    essay_service_factory: Optional[EssayServiceFactory] = None


def _create_cv_repository(user_id: int) -> ICVRepository:
    """Create a CV repository for a specific user."""
    orchestrator = container.orchestrator()
    cv_path = orchestrator.get_cv_path(user_id)
    cv_repository_class = container.cv_repository()
    return cv_repository_class(cv_path)


def _create_essay_service() -> IEssaySearchService:
    """Create an essay search service instance."""
    return container.essay_search_service()


def build_dependencies() -> BotDependencies:
    return BotDependencies(
        orchestrator_factory=container.orchestrator,
        cv_repository_factory=_create_cv_repository,
        essay_service_factory=_create_essay_service,
    )


def get_dependencies(context: Any) -> BotDependencies:
    return context.application.bot_data["dependencies"]
