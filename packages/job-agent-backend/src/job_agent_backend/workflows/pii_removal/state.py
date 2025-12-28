"""State definition for the PII removal workflow.

This module defines the state schema that flows through the langgraph workflow.
"""

from typing import Any, Callable, Dict, cast
from typing_extensions import TypeAlias, TypedDict

from langgraph.graph._node import _Node


class PIIRemovalState(TypedDict):
    """State schema for PII removal workflow.

    Attributes:
        cv_context: CV/resume content to process
    """

    cv_context: str


# Type alias for LangGraph node functions
NodeFunc: TypeAlias = _Node[PIIRemovalState]


def as_node(fn: Callable[[Dict[str, Any]], Any]) -> NodeFunc:
    """
    Wrap a node function for LangGraph type compatibility.

    LangGraph's add_node() expects _Node[State] protocol, but our node functions
    return specific TypedDict types. This helper casts the function to satisfy
    mypy --strict while preserving runtime behavior.

    Args:
        fn: Node function that takes state dict and returns a partial state update

    Returns:
        Same function cast to NodeFunc for LangGraph compatibility
    """
    return cast(NodeFunc, fn)
