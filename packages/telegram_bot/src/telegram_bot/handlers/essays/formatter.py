"""Formatter for essays listing handler.

This module provides formatting functions for displaying essays
in a paginated list format.
"""

from typing import List, Optional

from telegram import InlineKeyboardButton

from job_agent_platform_contracts.essay_repository.schemas import Essay
from telegram_bot.handlers.essays.messages import (
    PAGE_HEADER,
    EMPTY_LIST,
    BTN_PREVIOUS,
    BTN_NEXT,
    BTN_DELETE,
)


ANSWER_PREVIEW_LENGTH = 100


def format_essay_item(essay: Essay, index: int) -> str:
    """Format a single essay for display in the list.

    Args:
        essay: The essay to format
        index: The display index (1-based)

    Returns:
        Formatted string for the essay
    """
    parts = [f"{index}. "]

    if essay.question:
        parts.append(f"Q: {essay.question}\n")

    answer = essay.answer
    if len(answer) > ANSWER_PREVIEW_LENGTH:
        answer = answer[:ANSWER_PREVIEW_LENGTH] + "..."
    parts.append(f"A: {answer}")

    if essay.keywords and len(essay.keywords) > 0:
        keywords_str = ", ".join(essay.keywords)
        parts.append(f"\nKeywords: {keywords_str}")

    return "".join(parts)


def format_essays_page(essays: List[Essay], page: int, total_pages: int) -> str:
    """Format a page of essays with header.

    Args:
        essays: List of essays to display
        page: Current page number (1-based)
        total_pages: Total number of pages

    Returns:
        Formatted string for the entire page
    """
    if not essays:
        return EMPTY_LIST

    header = PAGE_HEADER.format(page=page, total_pages=total_pages)

    formatted_essays = []
    for idx, essay in enumerate(essays, start=1):
        formatted_essays.append(format_essay_item(essay, idx))

    return header + "\n\n" + "\n\n".join(formatted_essays)


def build_navigation_keyboard(
    page: int, total_pages: int, essays: Optional[List[Essay]] = None
) -> List[List[InlineKeyboardButton]]:
    """Build inline keyboard for pagination navigation and delete buttons.

    Args:
        page: Current page number (1-based)
        total_pages: Total number of pages
        essays: Optional list of essays to add delete buttons for

    Returns:
        List of button rows for InlineKeyboardMarkup
    """
    buttons = []

    # Add delete buttons for each essay
    if essays:
        for idx, essay in enumerate(essays, start=1):
            delete_button = InlineKeyboardButton(
                text=f"{BTN_DELETE} #{idx}",
                callback_data=f"essay_delete_{essay.id}",
            )
            buttons.append([delete_button])

    # Add navigation buttons
    if page > 1:
        prev_button = InlineKeyboardButton(
            text=f"< {BTN_PREVIOUS}",
            callback_data=f"essays_page_{page - 1}",
        )
    else:
        prev_button = InlineKeyboardButton(
            text=f"< {BTN_PREVIOUS}",
            callback_data="essays_noop_prev",
        )

    if page < total_pages:
        next_button = InlineKeyboardButton(
            text=f"{BTN_NEXT} >",
            callback_data=f"essays_page_{page + 1}",
        )
    else:
        next_button = InlineKeyboardButton(
            text=f"{BTN_NEXT} >",
            callback_data="essays_noop_next",
        )

    buttons.append([prev_button, next_button])

    return buttons
