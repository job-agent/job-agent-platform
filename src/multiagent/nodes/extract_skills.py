"""Extract skills node for the multiagent workflow.

This node extracts must-have skills from job descriptions using OpenAI.
"""

import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from ..state import AgentState


def extract_skills_node(state: AgentState) -> AgentState:
    """
    Extract must-have skills from job descriptions using OpenAI.

    This node processes each job's description field and uses an LLM to identify
    and extract the required/must-have skills mentioned in the job posting.

    Args:
        state: Current agent state containing the list of jobs

    Returns:
        Updated agent state with extracted_skills populated
    """
    jobs = state["jobs"]

    print(f"\n{'='*60}")
    print(f"Extracting must-have skills from {len(jobs)} jobs using OpenAI...")
    print(f"{'='*60}\n")

    # Initialize OpenAI chat model
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # Create prompt template for skill extraction
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert at analyzing job descriptions and extracting required skills.
Your task is to identify and list ONLY the must-have/required technical skills from the job description.
Do NOT include nice-to-have skills, soft skills, or responsibilities.

Return the skills as a comma-separated list, with each skill on the same line.
Example output: Python, Django, PostgreSQL, Docker, AWS"""),
        ("user", "Job Description:\n\n{description}")
    ])

    # Create the chain
    chain = prompt | llm | StrOutputParser()

    # Extract skills for each job
    extracted_skills = {}

    for idx, job in enumerate(jobs, 1):
        job_id = job.get("job_id")
        description = job.get("description", "")

        if not description:
            print(f"  Job #{idx} (ID: {job_id}): No description available, skipping...")
            extracted_skills[job_id] = []
            continue

        try:
            # Invoke the LLM to extract skills
            result = chain.invoke({"description": description})

            # Parse the comma-separated skills into a list
            skills = [skill.strip() for skill in result.split(",") if skill.strip()]

            extracted_skills[job_id] = skills

            print(f"  Job #{idx} (ID: {job_id}): Extracted {len(skills)} skills")
            print(f"    Skills: {', '.join(skills)}\n")

        except Exception as e:
            print(f"  Job #{idx} (ID: {job_id}): Error extracting skills - {str(e)}")
            extracted_skills[job_id] = []

    print(f"{'='*60}")
    print(f"Finished extracting skills from {len(jobs)} jobs")
    print(f"{'='*60}\n")

    return {
        "jobs": jobs,
        "status": state.get("status", "in_progress"),
        "extracted_skills": extracted_skills
    }
