"""Formatter for search essays handler.

This module provides formatting functions for displaying essay search results.
"""

from typing import List, Optional, Protocol, runtime_checkable

from telegram_bot.handlers.search_essays.messages import (
    NO_RESULTS,
    RESULTS_HEADER,
    NO_KEYWORDS,
    ANSWER_TRUNCATION_INDICATOR,
)


ANSWER_MAX_LENGTH = 500


@runtime_checkable
class EssayLike(Protocol):
    """Protocol for Essay objects."""

    id: int
    question: Optional[str]
    answer: str
    keywords: Optional[List[str]]


@runtime_checkable
class EssaySearchResultLike(Protocol):
    """Protocol for EssaySearchResult objects."""

    essay: EssayLike
    score: float


def format_search_result_item(result: EssaySearchResultLike) -> str:
    """Format a single search result for display.

    Args:
        result: The search result containing essay and scores

    Returns:
        Formatted string for the essay search result
    """
    essay = result.essay
    parts = []

    if essay.question:
        parts.append(f"**Question:** {essay.question}")

    answer = essay.answer
    if len(answer) > ANSWER_MAX_LENGTH:
        answer = answer[:ANSWER_MAX_LENGTH] + ANSWER_TRUNCATION_INDICATOR

    parts.append(f"**Answer:** {answer}")

    if essay.keywords and len(essay.keywords) > 0:
        keywords_str = ", ".join(essay.keywords)
        parts.append(f"**Keywords:** {keywords_str}")
    else:
        parts.append(f"**Keywords:** {NO_KEYWORDS}")

    return "\n".join(parts)


def format_search_results(results: List[EssaySearchResultLike]) -> str:
    """Format a list of search results for display.

    Args:
        results: List of search results to format

    Returns:
        Formatted string containing all results with header
    """
    if not results:
        return NO_RESULTS

    header = RESULTS_HEADER.format(count=len(results))

    formatted_items = []
    for result in results:
        formatted_items.append(format_search_result_item(result))

    separator = "\n\n---\n\n"
    body = separator.join(formatted_items)

    return f"{header}\n\n{body}"
