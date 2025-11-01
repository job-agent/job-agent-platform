"""Start command handler for Telegram bot."""

from telegram import Update
from telegram.ext import ContextTypes


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Hello {user.first_name}!\n\n"
        "I'm the Job Agent Bot. I help you find and analyze job opportunities "
        "that match your profile.\n\n"
        "Use /help to see available commands."
    )
