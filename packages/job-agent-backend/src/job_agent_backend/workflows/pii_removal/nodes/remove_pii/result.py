"""Result type for remove_pii node."""

from typing_extensions import TypedDict


class RemovePIIResult(TypedDict):
    """Result from remove_pii node."""

    cv_context: str
