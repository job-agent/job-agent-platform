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
        Updated state with job status marked as "irrelevant" if not relevant,
        otherwise status remains unchanged
    """
    job = state["job"]
    job_id = job.get("job_id")
    cv_context = state.get("cv_context", "")

    print("\n" + "=" * 60)
    print(f"Checking relevance for job ID {job_id}...")
    print("=" * 60 + "\n")

    # If no CV context available, skip the check and assume relevant
    if not cv_context:
        print(f"  Job (ID: {job_id}): No CV context available, assuming relevant")
        print("=" * 60 + "\n")
        return {
            "status": state.get("status", "in_progress"),
        }

    # Extract job details
    job_title = job.get("title", "Unknown")
    job_company = job.get("company", "Unknown")
    job_description = job.get("description", "")

    if not job_description:
        print(f"  Job (ID: {job_id}): No description available, assuming relevant")
        print("=" * 60 + "\n")
        return {
            "status": state.get("status", "in_progress"),
        }

    try:
        # Initialize LLM with structured output
        base_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        structured_llm = base_llm.with_structured_output(JobRelevance)

        # Prepare and invoke the prompt
        messages = CHECK_JOB_RELEVANCE_PROMPT.invoke(
            {
                "cv_content": cv_context,
                "job_title": job_title,
                "job_company": job_company,
                "job_description": job_description,
            }
        )

        result: JobRelevance = structured_llm.invoke(messages)

        # Log the result
        relevance_status = "RELEVANT" if result.is_relevant else "IRRELEVANT"
        print(f"  Job (ID: {job_id}): {relevance_status}")

        # Update status if irrelevant
        new_status = state.get("status", "in_progress")
        if not result.is_relevant:
            new_status = "irrelevant"

    except Exception as e:
        print(f"  Job (ID: {job_id}): Error checking relevance - {e}")
        print("    Assuming relevant by default\n")
        new_status = state.get("status", "in_progress")

    print("=" * 60)
    print(f"Finished checking relevance for job ID {job_id}")
    print("=" * 60 + "\n")

    return {
        "status": new_status,
    }
