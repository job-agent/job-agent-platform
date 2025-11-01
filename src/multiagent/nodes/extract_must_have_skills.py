"""Extract skills node for the multiagent workflow.

This node extracts must-have skills from job descriptions using OpenAI.
"""

import os

from langchain_openai import ChatOpenAI

from ..state import AgentState
from ..schemas import SkillsExtraction
from ..prompts import EXTRACT_MUST_HAVE_SKILLS_PROMPT


def extract_must_have_skills_node(state: AgentState) -> AgentState:
    jobs = state["jobs"]

    print("\n" + "=" * 60)
    print(f"Extracting must-have skills from {len(jobs)} jobs using OpenAI...")
    print("=" * 60 + "\n")

    base_llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    structured_llm = base_llm.with_structured_output(SkillsExtraction)

    prompt = EXTRACT_MUST_HAVE_SKILLS_PROMPT

    extracted_skills: dict[str, list[str]] = {}

    for idx, job in enumerate(jobs, 1):
        job_id = job.get("job_id")
        description = job.get("description", "")

        if not description:
            print(f"  Job #{idx} (ID: {job_id}): No description available, skipping...")
            extracted_skills[job_id] = []
            continue

        try:
            messages = prompt.invoke({"job_description": description})
            result: SkillsExtraction = structured_llm.invoke(messages)

            skills = (result.skills or []) if hasattr(result, "skills") else []
            extracted_skills[job_id] = skills

            print(f"  Job #{idx} (ID: {job_id}): Extracted {len(skills)} skills")
            if skills:
                print(f"    Skills: {', '.join(skills)}\n")

        except Exception as e:
            print(f"  Job #{idx} (ID: {job_id}): Error extracting skills - {e}")
            extracted_skills[job_id] = []

    print("=" * 60)
    print(f"Finished extracting skills from {len(jobs)} jobs")
    print("=" * 60 + "\n")

    return {
        "jobs": jobs,
        "status": state.get("status", "in_progress"),
        "extracted_skills": extracted_skills,
    }
