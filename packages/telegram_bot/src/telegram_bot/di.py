from dataclasses import dataclass
from typing import Any, Callable, Optional, Protocol

from job_agent_backend.container import container
from job_agent_platform_contracts import IJobAgentOrchestrator


class OrchestratorFactory(Protocol):
    def __call__(
        self, *, logger: Optional[Callable[[str], None]] = None
    ) -> IJobAgentOrchestrator: ...


@dataclass(frozen=True)
class BotDependencies:
    orchestrator_factory: OrchestratorFactory


def build_dependencies() -> BotDependencies:
    return BotDependencies(orchestrator_factory=container.orchestrator)


def get_dependencies(context: Any) -> BotDependencies:
    return context.application.bot_data["dependencies"]
