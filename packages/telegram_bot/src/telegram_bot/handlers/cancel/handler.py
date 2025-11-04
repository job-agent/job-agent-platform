"""Cancel command handler for Telegram bot."""

from telegram import Update
from telegram.ext import ContextTypes

from .messages import CANCELLING_MESSAGE, NO_SEARCH_TO_CANCEL_MESSAGE
from ..state import active_searches


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /cancel command.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user_id = update.effective_user.id
    is_active = active_searches.get(user_id, False)

    if is_active:
        active_searches[user_id] = False
        await update.message.reply_text(CANCELLING_MESSAGE)
    else:
        await update.message.reply_text(NO_SEARCH_TO_CANCEL_MESSAGE)
