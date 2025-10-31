"""State definition for the multiagent system.

This module defines the state schema that flows through the langgraph workflow.
"""

from typing import List
from typing_extensions import TypedDict

from job_scrapper_contracts import JobDict


class AgentState(TypedDict):
    """
    State schema for the multiagent workflow.

    Attributes:
        jobs: List of job dictionaries to process
        status: Current status of the workflow
    """
    jobs: List[JobDict]
    status: str
