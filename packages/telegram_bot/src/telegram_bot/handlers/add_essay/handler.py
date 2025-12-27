"""Handler for adding essays via Telegram."""

import re
from typing import Any, Optional, Tuple

from telegram import Update
from telegram.ext import ContextTypes

from job_agent_platform_contracts.essay_repository import EssayValidationError

from telegram_bot.handlers.add_essay import messages
from telegram_bot.di import get_dependencies


def _parse_essay_content(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse essay content to extract question and answer.

    Supports two formats:
    1. Question: <text> Answer: <text>
    2. Answer: <text> (answer-only)

    Markers are case-insensitive.

    Args:
        text: The raw message text (with command stripped)

    Returns:
        Tuple of (question, answer) where question may be None/empty
        Returns (None, None) if Answer: marker is not found
    """
    # Case-insensitive regex patterns
    # We use the LAST occurrence of Answer: to handle cases where
    # "Answer:" appears in the question content
    answer_pattern = re.compile(r"answer:", re.IGNORECASE)
    question_pattern = re.compile(r"question:", re.IGNORECASE)

    # Find all Answer: occurrences - we use the LAST one as the actual marker
    answer_matches = list(answer_pattern.finditer(text))
    if not answer_matches:
        return None, None

    # Use the last Answer: match
    answer_match = answer_matches[-1]
    answer_start = answer_match.end()
    answer = text[answer_start:].strip()

    # Everything before the last Answer: is candidate for Question
    before_answer = text[: answer_match.start()]

    # Look for Question: marker in the part before Answer:
    question_match = question_pattern.search(before_answer)
    if question_match:
        question_start = question_match.end()
        question = before_answer[question_start:].strip()
    else:
        question = None

    # Handle empty question (just "Question:" with no text)
    if question == "":
        question = None

    return question, answer


async def add_essay_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /add_essay command and essay content.

    Args:
        update: The update object containing the message
        context: The context object for the handler
    """
    # Guard clause for null message
    if not update.message:
        return

    message_text = update.message.text or ""

    # Strip the command prefix to get content
    # Handle both "/add_essay content" and "/add_essay"
    content = ""
    if message_text.startswith("/add_essay"):
        content = message_text[len("/add_essay") :].strip()

    # If no content provided, show instructions
    if not content:
        await update.message.reply_text(messages.INFO_INSTRUCTIONS)
        return

    # Parse the content for Question: and Answer: markers
    question, answer = _parse_essay_content(content)

    # Validate: Answer marker must be present
    if answer is None:
        await update.message.reply_text(messages.ERROR_INVALID_FORMAT)
        return

    # Validate: Answer must not be empty
    if not answer.strip():
        await update.message.reply_text(messages.ERROR_ANSWER_EMPTY)
        return

    # Show processing message
    processing_msg = await update.message.reply_text(messages.INFO_PROCESSING)

    try:
        # Get essay service from DI
        dependencies = get_dependencies(context)
        if dependencies.essay_service_factory is None:
            await processing_msg.edit_text(messages.ERROR_PROCESSING_FAILED)
            return
        essay_service = dependencies.essay_service_factory()

        # Prepare essay data
        essay_data: dict[str, Any] = {
            "answer": answer.strip(),
        }
        if question:
            essay_data["question"] = question.strip()

        # Create the essay
        essay = essay_service.create(essay_data)

        # Show success message with essay ID
        await processing_msg.edit_text(messages.SUCCESS_MESSAGE.format(id=essay.id))

    except EssayValidationError as e:
        await processing_msg.edit_text(messages.ERROR_VALIDATION_FAILED.format(message=str(e)))

    except Exception:
        # Generic error - don't expose internal details
        await processing_msg.edit_text(messages.ERROR_PROCESSING_FAILED)
