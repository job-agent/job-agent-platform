"""Main workflows system interface.

This module provides the public API for running the workflows system.
"""

import logging
import os
from typing import Callable, Optional, cast

from langchain_core.runnables import RunnableConfig

from job_agent_platform_contracts import IJobRepository

from job_scrapper_contracts import JobDict

from job_agent_backend.contracts import IModelFactory
from .job_processing import create_workflow
from .state import AgentState

logger = logging.getLogger(__name__)


def run_job_processing(
    job: JobDict,
    cv_content: str,
    job_repository_factory: Callable[[], IJobRepository],
    model_factory: Optional[IModelFactory] = None,
) -> AgentState:
    """
    Run the workflows system on a single job.

    This is the main entry point for the workflows system. It accepts a single
    job dictionary and processes it through the langgraph workflow.

    Args:
        job: A single job dictionary to process
        cv_content: The CV content to match against the job
        job_repository_factory: Factory for producing job repository instances
        model_factory: Factory for creating AI model instances. If not provided,
                       will be resolved from the DI container.

    Returns:
        Final agent state containing job processing results including:
        - is_relevant: Whether the job is relevant to the candidate
        - extracted_must_have_skills: List of must-have skills (for relevant jobs)
        - extracted_nice_to_have_skills: List of nice-to-have skills (for relevant jobs)
        - status: Final workflow status

    Raises:
        ValueError: If cv_content is empty or None

    Example:
        >>> job = {"title": "Python Developer", "salary": 5000}
        >>> cv_content = "My CV content..."
        >>> result = run_job_processing(job, cv_content)
        >>> if result.get("is_relevant"):
        >>>     print(f"Relevant job with skills: {result.get('extracted_must_have_skills')}")
    """

    tracing_enabled = os.getenv("LANGSMITH_TRACING_V2", "").lower() == "true"
    project_name = os.getenv("LANGSMITH_PROJECT", "default")

    if tracing_enabled:
        logger.info("LangSmith tracing enabled - Project: %s", project_name)
        logger.info("View traces at: https://smith.langchain.com/")

    if not cv_content:
        raise ValueError("CV content is required but was not provided")

    if not callable(job_repository_factory):
        raise ValueError("job_repository_factory must be callable")

    # Resolve model_factory from container if not provided
    resolved_model_factory = model_factory
    if resolved_model_factory is None:
        from job_agent_backend.container import container

        resolved_model_factory = container.model_factory()

    workflow_config: RunnableConfig = {
        "configurable": {
            "job_repository_factory": job_repository_factory,
            "model_factory": resolved_model_factory,
        }
    }

    workflow = create_workflow(workflow_config)

    initial_state: AgentState = {
        "job": job,
        "status": "started",
        "cv_context": cv_content,
    }

    final_state = cast(AgentState, workflow.invoke(initial_state))

    logger.info("Workflow completed with status: %s", final_state["status"])

    return final_state
