"""Result type for print_jobs node."""

from typing_extensions import TypedDict


class ProcessJobsResult(TypedDict):
    """Result from print_jobs (process_jobs) node."""

    status: str
