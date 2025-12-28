"""Extract nice-to-have skills node implementation."""

from typing import Callable

from .....model_providers import IModelFactory
from ...state import AgentState
from ..extract_must_have_skills.schemas import SkillsExtraction
from .prompts import EXTRACT_NICE_TO_HAVE_SKILLS_PROMPT
from .result import ExtractNiceToHaveSkillsResult


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

        print("\n" + "=" * 60)
        print(f"Extracting nice-to-have skills for job ID {job_id} using OpenAI...")
        print("=" * 60 + "\n")

        if not description:
            print(f"  Job (ID: {job_id}): No description available, skipping...")
            print("=" * 60 + "\n")
            return {"extracted_nice_to_have_skills": []}

        try:
            base_model = model_factory.get_model(model_id="skill-extraction")
            structured_model = base_model.with_structured_output(SkillsExtraction)
            prompt = EXTRACT_NICE_TO_HAVE_SKILLS_PROMPT

            messages = prompt.invoke({"job_description": description})
            raw_result = structured_model.invoke(messages)
            result = raw_result if isinstance(raw_result, SkillsExtraction) else None

            skills = (result.skills or []) if result is not None else []

            # Count total individual skills across all groups for logging
            total_skills = sum(len(group) for group in skills)
            print(
                f"  Job (ID: {job_id}): Extracted {total_skills} nice-to-have skills in {len(skills)} groups"
            )
            if skills:
                # Format 2D skills: show OR groups with " or " and AND groups with ", "
                formatted = ", ".join(
                    " or ".join(group) if len(group) > 1 else group[0] for group in skills if group
                )
                print(f"    Skills: {formatted}\n")

        except Exception as e:
            print(f"  Job (ID: {job_id}): Error extracting nice-to-have skills - {e}")
            skills = []

        print("=" * 60)
        print(f"Finished extracting nice-to-have skills for job ID {job_id}")
        print("=" * 60 + "\n")

        return {"extracted_nice_to_have_skills": skills}

    return extract_nice_to_have_skills_node
