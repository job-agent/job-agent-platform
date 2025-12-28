"""State definition for the workflows system.

This module defines the state schema that flows through the langgraph workflow.
"""

from typing import Any, Callable, List, cast
from typing_extensions import TypeAlias, TypedDict, NotRequired

from langgraph.graph._node import _Node
from job_scrapper_contracts import JobDict


class AgentState(TypedDict):
    """
    State schema for the workflows workflow.

    Attributes:
        job: Single job dictionary to process
        status: Current status of the workflow
        cv_context: CV/resume content for context
        is_relevant: Whether the job is relevant to the candidate's CV (optional)
        extracted_must_have_skills: List of extracted must-have skills (optional)
        extracted_nice_to_have_skills: List of extracted nice-to-have skills (optional)
    """

    job: JobDict
    status: str
    cv_context: str
    is_relevant: NotRequired[bool]
    extracted_must_have_skills: NotRequired[List[str]]
    extracted_nice_to_have_skills: NotRequired[List[str]]


# Type alias for LangGraph node functions
NodeFunc: TypeAlias = _Node[AgentState]


def as_node(fn: Callable[[AgentState], Any]) -> NodeFunc:
    """
    Wrap a node function for LangGraph type compatibility.

    LangGraph's add_node() expects _Node[State] protocol, but our node functions
    return specific TypedDict types. This helper casts the function to satisfy
    mypy --strict while preserving runtime behavior.

    Args:
        fn: Node function that takes AgentState and returns a partial state update

    Returns:
        Same function cast to NodeFunc for LangGraph compatibility
    """
    return cast(NodeFunc, fn)
