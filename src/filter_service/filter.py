"""Job filter service for filtering unsuitable job posts.

This module provides filtering capabilities for job posts coming from the
scrapper service before they are passed to the multiagent system.
"""

from typing import List, Optional
from typing_extensions import TypedDict

from job_scrapper_contracts import JobDict


class FilterConfig(TypedDict, total=False):
    """
    Configuration for job filtering.

    Attributes:
        max_months_of_experience: Maximum months of experience allowed (optional)
        location_allows_to_apply: Whether location allows to apply (optional)
    """
    max_months_of_experience: int
    location_allows_to_apply: bool


def filter_jobs(jobs: List[JobDict], config: Optional[FilterConfig] = None) -> List[JobDict]:
    """
    Filter unsuitable job posts from the list based on configuration criteria.

    If config is empty or None, all jobs are returned. Otherwise, jobs are
    filtered based on the provided criteria:
    - max_months_of_experience: Only includes jobs where experience_months <= max
    - location_allows_to_apply: If True, only includes jobs where location.can_apply is True

    Args:
        jobs: List of job dictionaries from the scrapper service
        config: Optional configuration for filtering criteria

    Returns:
        List[JobDict]: Filtered list of job dictionaries

    Example:
        >>> jobs = [
        ...     {"title": "Junior Dev", "experience_months": 12},
        ...     {"title": "Senior Dev", "experience_months": 48}
        ... ]
        >>> config = {"max_months_of_experience": 24}
        >>> filtered = filter_jobs(jobs, config)
        >>> len(filtered)
        1
    """
    if config is None or not config:
        return jobs

    filtered_jobs = []

    for job in jobs:
        # Check experience filter
        if "max_months_of_experience" in config:
            experience_months = job.get("experience_months", 0)
            if experience_months > config["max_months_of_experience"]:
                continue

        # Check location filter (only if explicitly set to True)
        if config.get("location_allows_to_apply"):
            location = job.get("location", {})
            can_apply = location.get("can_apply", False)
            if not can_apply:
                continue

        filtered_jobs.append(job)

    return filtered_jobs
