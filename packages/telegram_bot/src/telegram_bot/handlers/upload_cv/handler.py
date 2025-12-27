"""Handler for CV upload functionality."""

import tempfile
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.handlers.upload_cv import messages
from telegram_bot.di import get_dependencies


async def upload_cv_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle CV document uploads.

    Args:
        update: The update object containing the message
        context: The context object for the handler
    """
    if not update.message or not update.message.document or not update.effective_user:
        return

    user_id = update.effective_user.id
    document = update.message.document
    dependencies = get_dependencies(context)

    processing_msg = await update.message.reply_text(messages.INFO_PROCESSING)

    tmp_path = None
    try:
        file = await context.bot.get_file(document.file_id)

        file_extension = Path(document.file_name).suffix if document.file_name else ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            tmp_path = tmp_file.name
            await file.download_to_drive(tmp_path)

        orchestrator = dependencies.orchestrator_factory()
        orchestrator.upload_cv(user_id, tmp_path)

        Path(tmp_path).unlink()

        await processing_msg.edit_text(messages.SUCCESS_MESSAGE)

    except ValueError as e:
        print(f"Validation error handling CV upload: {e}")
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)
        await processing_msg.edit_text(messages.ERROR_VALIDATION_FAILED)
    except Exception as e:
        print(f"Error handling CV upload: {e}")
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)
        await processing_msg.edit_text(messages.ERROR_PROCESSING_FAILED)
