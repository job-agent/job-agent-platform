"""Schemas for extract_nice_to_have_skills node."""

from typing import List

from typing_extensions import TypedDict


class ExtractNiceToHaveSkillsResult(TypedDict):
    """Result type for extract_nice_to_have_skills node."""

    extracted_nice_to_have_skills: List[str]
