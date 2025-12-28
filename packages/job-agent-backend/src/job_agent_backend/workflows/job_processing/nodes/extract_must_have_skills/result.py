"""Result type for extract_must_have_skills node."""

from typing import List
from typing_extensions import TypedDict


class ExtractMustHaveSkillsResult(TypedDict):
    """Result from extract_must_have_skills node.

    The extracted skills use a 2D list format where:
    - The outer list represents AND relationships (all groups are required)
    - Inner lists represent OR relationships (alternatives within a group)
    """

    extracted_must_have_skills: List[List[str]]
