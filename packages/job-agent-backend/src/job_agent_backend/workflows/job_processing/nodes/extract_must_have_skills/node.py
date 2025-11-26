"""Extract must-have skills node implementation."""

from .....model_providers import get_model
from ...state import AgentState
from .schemas import SkillsExtraction
from .prompts import EXTRACT_MUST_HAVE_SKILLS_PROMPT


def extract_must_have_skills_node(state: AgentState) -> AgentState:
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
        return {
            "extracted_must_have_skills": [],
        }

    try:
        # Get model using configuration (defaults to "default" model if configured)
        # You can override by setting model_id to a specific configured model
        base_model = get_model(model_id="default", temperature=0)
        structured_model = base_model.with_structured_output(SkillsExtraction)
        prompt = EXTRACT_MUST_HAVE_SKILLS_PROMPT

        messages = prompt.invoke({"job_description": description})
        result: SkillsExtraction = structured_model.invoke(messages)

        skills = (result.skills or []) if hasattr(result, "skills") else []

        print(f"  Job (ID: {job_id}): Extracted {len(skills)} skills")
        if skills:
            print(f"    Skills: {', '.join(skills)}\n")

    except Exception as e:
        print(f"  Job (ID: {job_id}): Error extracting skills - {e}")
        skills = []

    print("=" * 60)
    print(f"Finished extracting skills for job ID {job_id}")
    print("=" * 60 + "\n")

    return {
        "extracted_must_have_skills": skills,
    }
