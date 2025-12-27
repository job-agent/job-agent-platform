"""Result type for check_job_relevance node."""

from typing_extensions import TypedDict


class CheckRelevanceResult(TypedDict):
    """Result from check_job_relevance node."""

    is_relevant: bool
