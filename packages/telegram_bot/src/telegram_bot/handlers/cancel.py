"""Cancel command handler for Telegram bot."""

from telegram import Update
from telegram.ext import ContextTypes

from .state import active_searches


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
        await update.message.reply_text(
            "🛑 Cancelling your job search...\n\n"
            "The search will stop after the current job finishes processing."
        )
    else:
        await update.message.reply_text(
            "ℹ️ No active search to cancel.\n\n" "Use /search to start a new job search."
        )
