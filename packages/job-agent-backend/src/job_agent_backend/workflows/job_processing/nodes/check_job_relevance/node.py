"""Check job relevance node implementation."""

import os

from langchain_openai import ChatOpenAI

from ...state import AgentState
from .schemas import JobRelevance
from .prompts import CHECK_JOB_RELEVANCE_PROMPT


def check_job_relevance_node(state: AgentState) -> AgentState:
    """
    Check if a job is relevant to the candidate based on their CV.

    This node uses an LLM to determine job relevance by comparing the job
    posting against the candidate's CV. It's configured to be lenient and
    default to marking jobs as relevant unless they're clearly mismatched.

    Args:
        state: Current agent state containing job and cv_context

    Returns:
        State update containing the "is_relevant" flag based on the LLM decision
    """
    job = state["job"]
    job_id = job.get("job_id")
    cv_context = state.get("cv_context", "")

    print("\n" + "=" * 60)
    print(f"Checking relevance for job ID {job_id}...")
    print("=" * 60 + "\n")

    if not cv_context:
        print(f"  Job (ID: {job_id}): No CV context available, assuming relevant")
        print("=" * 60 + "\n")
        return {
            "is_relevant": True,
        }

    job_title = job.get("title", "Unknown")
    job_company = job.get("company", "Unknown")
    job_description = job.get("description", "")

    if not job_description:
        print(f"  Job (ID: {job_id}): No description available, assuming relevant")
        print("=" * 60 + "\n")
        return {
            "is_relevant": True,
        }

    try:

        base_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        structured_llm = base_llm.with_structured_output(JobRelevance)

        messages = CHECK_JOB_RELEVANCE_PROMPT.invoke(
            {
                "cv_content": cv_context,
                "job_title": job_title,
                "job_company": job_company,
                "job_description": job_description,
            }
        )

        result: JobRelevance = structured_llm.invoke(messages)

        relevance_status = "RELEVANT" if result.is_relevant else "IRRELEVANT"
        print(f"  Job (ID: {job_id}): {relevance_status}")

        is_relevant = result.is_relevant

    except Exception as e:
        print(f"  Job (ID: {job_id}): Error checking relevance - {e}")
        print("    Assuming relevant by default\n")
        is_relevant = True

    print("=" * 60)
    print(f"Finished checking relevance for job ID {job_id}")
    print("=" * 60 + "\n")

    return {
        "is_relevant": is_relevant,
    }
