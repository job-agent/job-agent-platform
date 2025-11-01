"""State definition for the multiagent system.

This module defines the state schema that flows through the langgraph workflow.
"""

from typing import Dict, List
from typing_extensions import TypedDict, NotRequired

from job_scrapper_contracts import JobDict


class AgentState(TypedDict):
    """
    State schema for the multiagent workflow.

    Attributes:
        jobs: List of job dictionaries to process
        status: Current status of the workflow
        extracted_skills: Dictionary mapping job_id to list of extracted must-have skills (optional)
    """
    jobs: List[JobDict]
    status: str
    extracted_skills: NotRequired[Dict[int, List[str]]]
