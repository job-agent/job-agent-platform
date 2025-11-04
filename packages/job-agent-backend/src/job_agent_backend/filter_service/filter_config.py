"""Typed configuration for the filter service."""

from typing_extensions import TypedDict


class FilterConfig(TypedDict, total=False):
    """Configuration for job filtering."""

    max_months_of_experience: int
    location_allows_to_apply: bool
