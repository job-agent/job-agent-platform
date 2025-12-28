"""Extract must-have skills node implementation."""

from typing import Callable

from .....model_providers import IModelFactory
from ...state import AgentState
from .schemas import SkillsExtraction
from .prompts import EXTRACT_MUST_HAVE_SKILLS_PROMPT
from .result import ExtractMustHaveSkillsResult


def create_extract_must_have_skills_node(
    model_factory: IModelFactory,
) -> Callable[[AgentState], ExtractMustHaveSkillsResult]:
    """
    Factory function to create an extract_must_have_skills_node with injected dependencies.

    Args:
        model_factory: Factory used to create model instances

    Returns:
        Configured extract_must_have_skills_node function
    """

    def extract_must_have_skills_node(state: AgentState) -> ExtractMustHaveSkillsResult:
        """
        Extract must-have skills from a job description.

        Args:
            state: Current agent state containing job information

        Returns:
            Updated state with extracted skills
        """
        job = state["job"]
        job_id = job.get("job_id")
        description = job.get("description", "")

        print("\n" + "=" * 60)
        print(f"Extracting must-have skills for job ID {job_id} using OpenAI...")
        print("=" * 60 + "\n")

        if not description:
            print(f"  Job (ID: {job_id}): No description available, skipping...")
            print("=" * 60 + "\n")
            return {"extracted_must_have_skills": []}

        try:
            base_model = model_factory.get_model(model_id="skill-extraction")
            structured_model = base_model.with_structured_output(SkillsExtraction)
            prompt = EXTRACT_MUST_HAVE_SKILLS_PROMPT

            messages = prompt.invoke({"job_description": description})
            raw_result = structured_model.invoke(messages)
            result = raw_result if isinstance(raw_result, SkillsExtraction) else None

            skills = (result.skills or []) if result is not None else []

            print(f"  Job (ID: {job_id}): Extracted {len(skills)} skills")
            if skills:
                print(f"    Skills: {', '.join(skills)}\n")

        except Exception as e:
            print(f"  Job (ID: {job_id}): Error extracting skills - {e}")
            skills = []

        print("=" * 60)
        print(f"Finished extracting skills for job ID {job_id}")
        print("=" * 60 + "\n")

        return {"extracted_must_have_skills": skills}

    return extract_must_have_skills_node
