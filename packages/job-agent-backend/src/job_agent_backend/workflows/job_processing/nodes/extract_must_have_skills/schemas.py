"""Pydantic schemas for extract_must_have_skills node."""

from typing import List
from pydantic import BaseModel, Field


class SkillsExtraction(BaseModel):
    """Schema for extracting skills from job descriptions.

    This schema can be reused for different types of skill extraction:
    - Must-have/required skills
    - Nice-to-have/preferred skills
    - Any other skill categorization

    The skills are represented as a 2D list where:
    - The outer list represents AND relationships (all groups are required)
    - Inner lists represent OR relationships (alternatives within a group)

    Example: [["JavaScript", "Python"], ["React"], ["Docker", "Kubernetes"]]
    means "(JavaScript OR Python) AND React AND (Docker OR Kubernetes)"

    Attributes:
        skills: 2D list of extracted skill groups. Each inner list contains
            alternative skills (OR relationship), and the outer list contains
            groups that are all required (AND relationship).
    """

    skills: List[List[str]] = Field(
        description=(
            "2D list of skill groups extracted from the job description. "
            "Each inner list contains alternative skills (OR relationship), "
            "and all groups in the outer list are required (AND relationship). "
            "Solo skills should be wrapped in single-item inner lists. "
            "Example: [['JavaScript', 'Python'], ['React'], ['Docker', 'Kubernetes']]"
        ),
        default_factory=list,
    )
