"""Help command handler for Telegram bot."""

from telegram import Update
from telegram.ext import ContextTypes

from .messages import HELP_TEXT


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command.

    Args:
        update: Telegram update object
        context: Callback context
    """
    await update.message.reply_text(HELP_TEXT)
