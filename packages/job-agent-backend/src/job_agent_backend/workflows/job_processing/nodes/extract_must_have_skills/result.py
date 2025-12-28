"""Result type for extract_must_have_skills node."""

from typing import List
from typing_extensions import TypedDict


class ExtractMustHaveSkillsResult(TypedDict):
    """Result from extract_must_have_skills node."""

    extracted_must_have_skills: List[str]
