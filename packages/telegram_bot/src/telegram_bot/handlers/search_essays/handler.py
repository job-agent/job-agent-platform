"""Handler for /search_essays command."""

from typing import Optional, Tuple

from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.di import get_dependencies
from telegram_bot.handlers.search_essays.formatter import format_search_results
from telegram_bot.handlers.search_essays.messages import (
    USAGE_HELP,
    INVALID_LIMIT,
)


DEFAULT_LIMIT = 10
FIXED_VECTOR_WEIGHT = 0.5


def _parse_command_args(message_text: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    """Parse query and limit from command message text.

    The parsing strategy:
    - If the last argument is a valid positive integer, treat it as limit
    - Otherwise, include it in the query and use default limit
    - Multi-word queries are supported without quotes

    Args:
        message_text: The full message text including command

    Returns:
        Tuple of (query, limit, error_message). If error_message is not None,
        query and limit are invalid.
    """
    parts = message_text.split()

    if len(parts) <= 1:
        return None, None, USAGE_HELP

    command_args = parts[1:]

    last_arg = command_args[-1]
    try:
        limit = int(last_arg)
        if limit <= 0:
            return None, None, INVALID_LIMIT
        query_parts = command_args[:-1]
        if not query_parts:
            query = last_arg
            limit = DEFAULT_LIMIT
        else:
            query = " ".join(query_parts)
    except ValueError:
        query = " ".join(command_args)
        limit = DEFAULT_LIMIT

    if not query or not query.strip():
        return None, None, USAGE_HELP

    return query.strip(), limit, None


async def search_essays_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /search_essays command.

    Searches for essays using hybrid search and returns formatted results.

    Args:
        update: Telegram update object
        context: Telegram context object
    """
    if not update.message:
        return None

    message_text = update.message.text or ""
    query, limit, error = _parse_command_args(message_text)

    if error:
        await update.message.reply_text(error)
        return None

    dependencies = get_dependencies(context)
    essay_service = dependencies.essay_service_factory()

    results = essay_service.search(
        query=query,
        limit=limit,
        vector_weight=FIXED_VECTOR_WEIGHT,
    )

    response = format_search_results(results)
    await update.message.reply_text(response)
    return None
