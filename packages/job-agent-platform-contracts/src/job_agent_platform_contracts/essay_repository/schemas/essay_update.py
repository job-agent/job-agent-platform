"""Schema for updating an essay."""

from typing import List, TypedDict


class EssayUpdate(TypedDict, total=False):
    """Schema for updating an existing essay.

    All fields are optional to allow partial updates.
    """

    question: str
    answer: str
    keywords: List[str]
