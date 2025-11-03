"""Status command handler for Telegram bot."""

from telegram import Update
from telegram.ext import ContextTypes

from .messages import ACTIVE_SEARCH_MESSAGE, NO_ACTIVE_SEARCH_MESSAGE
from ..state import active_searches


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /status command.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user_id = update.effective_user.id
    is_active = active_searches.get(user_id, False)

    if is_active:
        await update.message.reply_text(ACTIVE_SEARCH_MESSAGE)
    else:
        await update.message.reply_text(NO_ACTIVE_SEARCH_MESSAGE)
