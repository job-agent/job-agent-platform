"""Schema for creating an essay."""

from typing import List, TypedDict


class EssayCreate(TypedDict, total=False):
    """Schema for creating a new essay.

    Required fields:
        answer: The response/essay content (required)

    Optional fields:
        question: The prompt or question being answered
        keywords: Tags or keywords associated with the essay
    """

    question: str
    answer: str  # Required, but TypedDict(total=False) allows validation at runtime
    keywords: List[str]
