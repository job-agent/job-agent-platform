from typing_extensions import NotRequired, TypedDict

from job_scrapper_contracts import JobDict


class JobProcessingResult(TypedDict):
    """Result from job processing workflow.

    The skill fields use a 2D list format where:
    - The outer list represents AND relationships (all groups are required/preferred)
    - Inner lists represent OR relationships (alternatives within a group)

    Example: [["JavaScript", "Python"], ["React"]] means
    "(JavaScript OR Python) AND React"
    """

    status: str
    job: NotRequired[JobDict]
    cv_context: NotRequired[str]
    is_relevant: NotRequired[bool]
    extracted_must_have_skills: NotRequired[list[list[str]]]
    extracted_nice_to_have_skills: NotRequired[list[list[str]]]
