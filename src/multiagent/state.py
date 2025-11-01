"""State definition for the multiagent system.

This module defines the state schema that flows through the langgraph workflow.
"""

from typing import List
from typing_extensions import TypedDict, NotRequired

from job_scrapper_contracts import JobDict


class AgentState(TypedDict):
    """
    State schema for the multiagent workflow.

    Attributes:
        job: Single job dictionary to process
        status: Current status of the workflow
        extracted_skills: List of extracted must-have skills (optional)
    """
    job: JobDict
    status: str
    extracted_skills: NotRequired[List[str]]
