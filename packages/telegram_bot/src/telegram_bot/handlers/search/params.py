"""Search parameter parsing for Telegram bot.

This module provides functions for parsing and validating search parameters
from user input arguments.
"""

from typing import Optional, Tuple, List
from typing_extensions import TypedDict


# Default search parameters
DEFAULT_MIN_SALARY = 4000
DEFAULT_EMPLOYMENT_LOCATION = "remote"
DEFAULT_TIMEOUT = 30


class SearchParams(TypedDict):
    """Type definition for search parameters."""

    min_salary: int
    employment_location: str
    days: Optional[int]
    timeout: int


class ParseError:
    """Represents a parsing error with user-friendly message."""

    def __init__(self, message: str):
        self.message = message


def get_default_params() -> SearchParams:
    """Get default search parameters.

    Returns:
        SearchParams with default values
    """
    return {
        "min_salary": DEFAULT_MIN_SALARY,
        "employment_location": DEFAULT_EMPLOYMENT_LOCATION,
        "days": None,
        "timeout": DEFAULT_TIMEOUT,
    }


def parse_search_params(args: List[str]) -> Tuple[Optional[SearchParams], Optional[ParseError]]:
    """Parse search parameters from command arguments.

    Parses key=value style arguments and returns validated SearchParams
    or an error if parsing fails.

    Args:
        args: List of argument strings (e.g., ["min_salary=5000", "days=7"])

    Returns:
        Tuple of (SearchParams, None) on success, or (None, ParseError) on failure

    Examples:
        >>> parse_search_params(["min_salary=5000"])
        ({'min_salary': 5000, 'employment_location': 'remote', 'days': None, 'timeout': 30}, None)

        >>> parse_search_params(["salary=5000"])
        (None, ParseError("The parameter 'salary' is no longer supported..."))
    """
    params = get_default_params()

    for arg in args:
        if "=" not in arg:
            continue

        key, value = arg.split("=", 1)

        # Handle deprecated parameter
        if key == "salary":
            return None, ParseError(
                "The parameter 'salary' is no longer supported. Please use 'min_salary'."
            )

        if key == "min_salary":
            try:
                params["min_salary"] = int(value)
            except ValueError:
                return None, ParseError(f"Invalid value for {key}: {value}. Must be a number.")
        elif key == "days":
            try:
                params["days"] = int(value)
            except ValueError:
                return None, ParseError(f"Invalid value for {key}: {value}. Must be a number.")
        elif key == "timeout":
            try:
                params["timeout"] = int(value)
            except ValueError:
                return None, ParseError(f"Invalid value for {key}: {value}. Must be a number.")
        elif key == "employment_location":
            params["employment_location"] = value

    return params, None
