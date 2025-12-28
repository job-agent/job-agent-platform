"""Handler for /essays command and pagination callbacks.

This module provides handlers for listing essays with pagination.
"""

import math

from telegram import Update, InlineKeyboardMarkup
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
)


PAGE_SIZE = 5


async def essays_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /essays command to show paginated essay list.

    Args:
        update: Telegram update object
        context: Telegram context object
    """
    if not update.message:
        return None

    dependencies = get_dependencies(context)
    essay_service = dependencies.essay_service_factory()

    try:
        essays, total_count = essay_service.get_paginated(page=1, page_size=PAGE_SIZE)
    except Exception:
        await update.message.reply_text(ERROR_LOADING)
        return

    if not essays and total_count == 0:
        await update.message.reply_text(EMPTY_LIST)
        return

    total_pages = math.ceil(total_count / PAGE_SIZE)
    message_text = format_essays_page(essays, page=1, total_pages=total_pages)
    keyboard = build_navigation_keyboard(page=1, total_pages=total_pages)

    await update.message.reply_text(
        message_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


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

    dependencies = get_dependencies(context)
    essay_service = dependencies.essay_service_factory()

    try:
        essays, total_count = essay_service.get_paginated(page=page, page_size=PAGE_SIZE)
    except Exception:
        await query.answer("Failed to load essays. Please try again.")
        return

    await query.answer()

    total_pages = math.ceil(total_count / PAGE_SIZE) if total_count > 0 else 1
    message_text = format_essays_page(essays, page=page, total_pages=total_pages)
    keyboard = build_navigation_keyboard(page=page, total_pages=total_pages)

    await query.edit_message_text(
        message_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
