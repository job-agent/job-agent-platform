"""Pydantic schemas for extract_must_have_skills node."""

from typing import List
from pydantic import BaseModel, Field


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
        default_factory=list,
    )
