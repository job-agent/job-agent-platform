from collections.abc import Mapping
from typing import Any, cast

from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph

from job_agent_backend.container import container
from job_agent_backend.workflows.job_processing.job_processing import create_workflow


def _prepare_config(config: RunnableConfig | None) -> RunnableConfig:
    prepared: dict[str, Any] = {}
    if isinstance(config, Mapping):
        prepared.update(config)
    configurable_source = prepared.get("configurable")
    configurable: dict[str, Any] = {}
    if isinstance(configurable_source, Mapping):
        configurable.update(configurable_source)
    factory = configurable.get("job_repository_factory")
    if not callable(factory):
        factory = container.job_repository_factory()
        if not callable(factory):
            raise ValueError("job_repository_factory provider returned a non-callable value")
        configurable["job_repository_factory"] = factory
    prepared["configurable"] = configurable
    return cast(RunnableConfig, prepared)


def create_workflow_with_dependencies(config: RunnableConfig | None = None) -> CompiledStateGraph:
    resolved_config = _prepare_config(config)
    return create_workflow(resolved_config)
