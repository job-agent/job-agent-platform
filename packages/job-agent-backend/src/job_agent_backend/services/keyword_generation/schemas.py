"""Pydantic schemas for keyword extraction."""

from typing import List
from pydantic import BaseModel, Field


class KeywordsExtraction(BaseModel):
    """Schema for extracting keywords from essay content.

    Attributes:
        keywords: List of extracted keywords
    """

    keywords: List[str] = Field(
        description="List of keywords extracted from the essay content.",
        default_factory=list,
    )
