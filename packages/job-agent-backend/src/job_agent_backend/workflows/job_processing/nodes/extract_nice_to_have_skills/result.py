"""Result type for extract_nice_to_have_skills node."""

from typing import List
from typing_extensions import TypedDict


class ExtractNiceToHaveSkillsResult(TypedDict):
    """Result from extract_nice_to_have_skills node.

    The extracted skills use a 2D list format where:
    - The outer list represents AND relationships (all groups are preferred)
    - Inner lists represent OR relationships (alternatives within a group)
    """

    extracted_nice_to_have_skills: List[List[str]]
