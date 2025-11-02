"""State definition for the workflows system.

This module defines the state schema that flows through the langgraph workflow.
"""

from typing import List, Any
from typing_extensions import TypedDict, NotRequired

from job_scrapper_contracts import JobDict


class AgentState(TypedDict):
    """
    State schema for the workflows workflow.

    Attributes:
        job: Single job dictionary to process
        status: Current status of the workflow
        cv_context: CV/resume content for context
        is_relevant: Whether the job is relevant to the candidate's CV (optional)
        extracted_skills: List of extracted must-have skills (optional)
        db_session: Database session for storing jobs (optional)
    """

    job: JobDict
    status: str
    cv_context: str
    is_relevant: NotRequired[bool]
    extracted_skills: NotRequired[List[str]]
    db_session: NotRequired[Any]
