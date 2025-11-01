"""State definition for the workflows system.

This module defines the state schema that flows through the langgraph workflow.
"""

from typing import List
from typing_extensions import TypedDict, NotRequired

from job_scrapper_contracts import JobDict


class AgentState(TypedDict):
    """
    State schema for the workflows workflow.

    Attributes:
        job: Single job dictionary to process
        status: Current status of the workflow
        cv_context: CV/resume content for context
        extracted_skills: List of extracted must-have skills (optional)
    """

    job: JobDict
    status: str
    cv_context: str
    extracted_skills: NotRequired[List[str]]
