"""Helper functions for E2E tests."""

import re


def extract_essay_id(response: str) -> int | None:
    """Extract essay ID from a bot response.

    Parses the response text looking for patterns like "ID: 123" or "ID:123"
    that indicate an essay ID in success messages.

    Args:
        response: The bot response text containing essay ID

    Returns:
        The extracted essay ID as integer, or None if not found

    Examples:
        >>> extract_essay_id("Essay saved successfully! (ID: 42)")
        42
        >>> extract_essay_id("No ID here")
        None
    """
    match = re.search(r"ID:\s*(\d+)", response, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None
