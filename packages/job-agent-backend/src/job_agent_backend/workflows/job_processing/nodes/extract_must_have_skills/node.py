"""Extract must-have skills node implementation."""

import os

from langchain_openai import ChatOpenAI

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
            "status": state.get("status", "in_progress"),
            "extracted_skills": [],
        }

    try:
        base_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        structured_llm = base_llm.with_structured_output(SkillsExtraction)
        prompt = EXTRACT_MUST_HAVE_SKILLS_PROMPT

        messages = prompt.invoke({"job_description": description})
        result: SkillsExtraction = structured_llm.invoke(messages)

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
        "status": state.get("status", "in_progress"),
        "extracted_skills": skills,
    }
