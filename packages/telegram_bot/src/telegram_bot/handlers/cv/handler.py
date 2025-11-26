"""CV command handler for Telegram bot."""

from io import BytesIO

from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.di import get_dependencies
from .messages import NO_CV_MESSAGE, CV_SENT_MESSAGE


async def cv_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /cv command.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user_id = update.effective_user.id
    dependencies = get_dependencies(context)
    cv_repository = dependencies.cv_repository_factory(user_id)

    cv_content = cv_repository.find()

    if cv_content is None:
        await update.message.reply_text(NO_CV_MESSAGE)
    else:
        # Send CV as a text file to avoid message length limits
        cv_bytes = BytesIO(cv_content.encode("utf-8"))
        cv_bytes.name = f"cv_{user_id}.txt"

        await update.message.reply_document(
            document=cv_bytes, filename=f"cv_{user_id}.txt", caption=CV_SENT_MESSAGE
        )
