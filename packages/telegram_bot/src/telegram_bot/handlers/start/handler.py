"""Start command handler for Telegram bot."""

from telegram import Update
from telegram.ext import ContextTypes

from .messages import get_welcome_message


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user = update.effective_user
    await update.message.reply_text(get_welcome_message(user.first_name))
