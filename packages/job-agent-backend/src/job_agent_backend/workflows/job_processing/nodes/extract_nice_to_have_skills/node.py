"""Extract nice-to-have skills node implementation."""

import os

from langchain_openai import ChatOpenAI

from ...state import AgentState
from ..extract_must_have_skills.schemas import SkillsExtraction
from .prompts import EXTRACT_NICE_TO_HAVE_SKILLS_PROMPT


def extract_nice_to_have_skills_node(state: AgentState) -> AgentState:
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
        return {
            "extracted_nice_to_have_skills": [],
        }

    try:
        base_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        structured_llm = base_llm.with_structured_output(SkillsExtraction)
        prompt = EXTRACT_NICE_TO_HAVE_SKILLS_PROMPT

        messages = prompt.invoke({"job_description": description})
        result: SkillsExtraction = structured_llm.invoke(messages)

        skills = (result.skills or []) if hasattr(result, "skills") else []

        print(f"  Job (ID: {job_id}): Extracted {len(skills)} nice-to-have skills")
        if skills:
            print(f"    Skills: {', '.join(skills)}\n")

    except Exception as e:
        print(f"  Job (ID: {job_id}): Error extracting nice-to-have skills - {e}")
        skills = []

    print("=" * 60)
    print(f"Finished extracting nice-to-have skills for job ID {job_id}")
    print("=" * 60 + "\n")

    return {
        "extracted_nice_to_have_skills": skills,
    }
