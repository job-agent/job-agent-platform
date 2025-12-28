"""Extract nice-to-have skills node implementation."""

import logging
from typing import Callable

from job_agent_backend.contracts import IModelFactory
from ...state import AgentState
from ..extract_must_have_skills.schemas import SkillsExtraction
from .prompts import EXTRACT_NICE_TO_HAVE_SKILLS_PROMPT
from .result import ExtractNiceToHaveSkillsResult

logger = logging.getLogger(__name__)


def create_extract_nice_to_have_skills_node(
    model_factory: IModelFactory,
) -> Callable[[AgentState], ExtractNiceToHaveSkillsResult]:
    """
    Factory function to create an extract_nice_to_have_skills_node with injected dependencies.

    Args:
        model_factory: Factory used to create model instances

    Returns:
        Configured extract_nice_to_have_skills_node function
    """

    def extract_nice_to_have_skills_node(state: AgentState) -> ExtractNiceToHaveSkillsResult:
        """
        Extract nice-to-have skills from a job description.

        Args:
            state: Current agent state containing job information

        Returns:
            Updated state with extracted nice-to-have skills
        """
        job = state["job"]
        job_id = job.get("job_id")
        description = job.get("description", "")

        logger.info("Extracting nice-to-have skills for job ID %s using OpenAI", job_id)

        if not description:
            logger.info("Job (ID: %s): No description available, skipping", job_id)
            return {"extracted_nice_to_have_skills": []}

        try:
            base_model = model_factory.get_model(model_id="skill-extraction")
            structured_model = base_model.with_structured_output(SkillsExtraction)
            prompt = EXTRACT_NICE_TO_HAVE_SKILLS_PROMPT

            messages = prompt.invoke({"job_description": description})
            raw_result = structured_model.invoke(messages)
            result = raw_result if isinstance(raw_result, SkillsExtraction) else None

            skills = (result.skills or []) if result is not None else []

            logger.info("Job (ID: %s): Extracted %d nice-to-have skills", job_id, len(skills))
            if skills:
                logger.debug("Skills: %s", ", ".join(skills))

        except Exception as e:
            logger.warning("Job (ID: %s): Error extracting nice-to-have skills - %s", job_id, e)
            skills = []

        logger.info("Finished extracting nice-to-have skills for job ID %s", job_id)

        return {"extracted_nice_to_have_skills": skills}

    return extract_nice_to_have_skills_node
