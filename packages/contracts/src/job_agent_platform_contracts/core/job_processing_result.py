from typing_extensions import NotRequired, TypedDict

from job_scrapper_contracts import JobDict


class JobProcessingResult(TypedDict):
    status: str
    job: NotRequired[JobDict]
    cv_context: NotRequired[str]
    is_relevant: NotRequired[bool]
    extracted_must_have_skills: NotRequired[list[str]]
    extracted_nice_to_have_skills: NotRequired[list[str]]
