"""Pydantic schemas for LLM structured outputs.

This module contains reusable schemas for extracting structured data from LLM responses.
"""

from typing import List
from pydantic import BaseModel, Field


__all__ = ["SkillsExtraction", "JobRelevance"]


class SkillsExtraction(BaseModel):
    """Schema for extracting skills from job descriptions.

    This schema can be reused for different types of skill extraction:
    - Must-have/required skills
    - Nice-to-have/preferred skills
    - Any other skill categorization

    Attributes:
        skills: List of extracted skill names
    """
    skills: List[str] = Field(
        description="List of skills extracted from the job description. Each skill should be concise and specific.",
        default_factory=list
    )


class JobRelevance(BaseModel):
    """Schema for determining job relevance based on CV.

    Attributes:
        is_relevant: Boolean indicating if the job is relevant to the candidate
    """
    is_relevant: bool = Field(
        description="True if the job is relevant to the candidate's profile, False if clearly irrelevant"
    )
