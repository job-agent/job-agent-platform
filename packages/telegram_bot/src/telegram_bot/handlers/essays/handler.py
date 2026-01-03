"""Handler for /essays command and pagination callbacks.

This module provides handlers for listing essays with pagination.
"""

import math
from typing import Tuple, Optional

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from telegram_bot.di import get_dependencies
from telegram_bot.handlers.essays.formatter import (
    format_essays_page,
    build_navigation_keyboard,
)
from telegram_bot.handlers.essays.messages import (
    EMPTY_LIST,
    ERROR_LOADING,
    MSG_FIRST_PAGE,
    MSG_LAST_PAGE,
    CONFIRM_DELETE_PROMPT,
    BTN_CONFIRM_DELETE,
    BTN_CANCEL_DELETE,
    MSG_ESSAY_DELETED,
    MSG_ESSAY_NOT_FOUND,
    MSG_DELETE_FAILED,
)


PAGE_SIZE = 5


def _build_essay_list_content(
    context: ContextTypes.DEFAULT_TYPE, page: int = 1
) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
    """Build essay list content for display.

    Args:
        context: Telegram context object
        page: Page number to display (1-based)

    Returns:
        Tuple of (message_text, reply_markup)

    Raises:
        Exception: If service call fails (caller should handle)
    """
    dependencies = get_dependencies(context)
    essay_service = dependencies.essay_service_factory()

    essays, total_count = essay_service.get_paginated(page=page, page_size=PAGE_SIZE)

    if not essays and total_count == 0:
        return EMPTY_LIST, None

    total_pages = math.ceil(total_count / PAGE_SIZE) if total_count > 0 else 1
    message_text = format_essays_page(essays, page=page, total_pages=total_pages)
    keyboard = build_navigation_keyboard(page=page, total_pages=total_pages, essays=essays)

    return message_text, InlineKeyboardMarkup(keyboard)


async def essays_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /essays command to show paginated essay list.

    Args:
        update: Telegram update object
        context: Telegram context object
    """
    if not update.message:
        return None

    try:
        message_text, reply_markup = _build_essay_list_content(context, page=1)
    except Exception:
        await update.message.reply_text(ERROR_LOADING)
        return

    await update.message.reply_text(message_text, reply_markup=reply_markup)


async def essays_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback queries for essays pagination.

    Args:
        update: Telegram update object
        context: Telegram context object
    """
    query = update.callback_query
    if not query:
        return None

    callback_data = query.data

    if callback_data == "essays_noop_prev":
        await query.answer(MSG_FIRST_PAGE)
        return

    if callback_data == "essays_noop_next":
        await query.answer(MSG_LAST_PAGE)
        return

    if not callback_data or not callback_data.startswith("essays_page_"):
        await query.answer()
        return

    try:
        page = int(callback_data.replace("essays_page_", ""))
    except ValueError:
        await query.answer()
        return

    try:
        message_text, reply_markup = _build_essay_list_content(context, page=page)
    except Exception:
        await query.answer("Failed to load essays. Please try again.")
        return

    await query.answer()
    await query.edit_message_text(message_text, reply_markup=reply_markup)


async def essays_delete_callback_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle callback for essay delete button.

    Shows confirmation prompt with Confirm/Cancel buttons.

    Args:
        update: Telegram update object
        context: Telegram context object
    """
    query = update.callback_query
    if not query:
        return None

    callback_data = query.data

    if not callback_data or not callback_data.startswith("essay_delete_"):
        await query.answer()
        return

    try:
        essay_id = int(callback_data.replace("essay_delete_", ""))
    except ValueError:
        await query.answer()
        return

    await query.answer()

    confirmation_text = CONFIRM_DELETE_PROMPT.format(essay_id=essay_id)
    keyboard = [
        [
            InlineKeyboardButton(
                BTN_CONFIRM_DELETE, callback_data=f"essay_delete_confirm_{essay_id}"
            ),
            InlineKeyboardButton(BTN_CANCEL_DELETE, callback_data="essay_delete_cancel"),
        ]
    ]

    await query.edit_message_text(
        confirmation_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def essays_delete_confirm_callback_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle callback for confirming essay deletion.

    Deletes the essay and refreshes the list.

    Args:
        update: Telegram update object
        context: Telegram context object
    """
    query = update.callback_query
    if not query:
        return None

    callback_data = query.data

    if not callback_data or not callback_data.startswith("essay_delete_confirm_"):
        await query.answer()
        return

    try:
        essay_id = int(callback_data.replace("essay_delete_confirm_", ""))
    except ValueError:
        await query.answer()
        return

    dependencies = get_dependencies(context)
    essay_service = dependencies.essay_service_factory()

    try:
        deleted = essay_service.delete(essay_id)
    except Exception:
        await query.answer(MSG_DELETE_FAILED)
        return

    if not deleted:
        await query.answer(MSG_ESSAY_NOT_FOUND)
        return

    await query.answer(MSG_ESSAY_DELETED)

    try:
        message_text, reply_markup = _build_essay_list_content(context, page=1)
    except Exception:
        await query.answer(MSG_DELETE_FAILED)
        return

    await query.edit_message_text(message_text, reply_markup=reply_markup)


async def essays_delete_cancel_callback_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle callback for cancelling essay deletion.

    Returns to the essay list view.

    Args:
        update: Telegram update object
        context: Telegram context object
    """
    query = update.callback_query
    if not query:
        return None

    await query.answer()

    try:
        message_text, reply_markup = _build_essay_list_content(context, page=1)
    except Exception:
        await query.answer(MSG_DELETE_FAILED)
        return

    await query.edit_message_text(message_text, reply_markup=reply_markup)
