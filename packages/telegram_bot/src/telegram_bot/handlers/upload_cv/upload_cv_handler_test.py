"""Tests for upload CV handler."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from telegram_bot.conftest import MockContext, MockDocument, MockFile
from telegram_bot.handlers.upload_cv.handler import upload_cv_handler
from telegram_bot.handlers.upload_cv import messages


@pytest.fixture
def mock_bot_with_file():
    """Create a mock bot that returns a mock file."""
    bot = MagicMock()
    bot.get_file = AsyncMock(return_value=MockFile())
    return bot


class TestUploadCvHandler:
    """Tests for upload_cv_handler function."""

    async def test_returns_early_when_no_message(self, handler_test_setup_factory):
        """Handler should return early when update has no message."""
        setup = handler_test_setup_factory(user_id=6001)
        update = MagicMock()
        update.message = None

        result = await upload_cv_handler(update, setup.context)

        assert result is None

    async def test_returns_early_when_no_document(self, handler_test_setup_factory):
        """Handler should return early when message has no document."""
        setup = handler_test_setup_factory(user_id=6001, document=None)

        result = await upload_cv_handler(setup.update, setup.context)

        assert result is None

    async def test_sends_processing_message(
        self, handler_test_setup_factory, mock_bot_with_file, mock_orchestrator
    ):
        """Handler should send processing message first."""
        document = MockDocument(file_name="test.pdf")
        setup = handler_test_setup_factory(user_id=6002, document=document)
        setup.context.bot = mock_bot_with_file

        await upload_cv_handler(setup.update, setup.context)

        assert messages.INFO_PROCESSING in setup.message._reply_texts

    async def test_downloads_file_from_telegram(
        self, handler_test_setup_factory, mock_bot_with_file, mock_orchestrator
    ):
        """Handler should download the file from Telegram."""
        document = MockDocument(file_id="test_file_123", file_name="cv.pdf")
        setup = handler_test_setup_factory(user_id=6003, document=document)
        setup.context.bot = mock_bot_with_file

        await upload_cv_handler(setup.update, setup.context)

        mock_bot_with_file.get_file.assert_called_once_with(document.file_id)

    async def test_calls_orchestrator_upload_cv(
        self, handler_test_setup_factory, mock_bot_with_file, mock_orchestrator
    ):
        """Handler should call orchestrator.upload_cv with correct arguments."""
        document = MockDocument(file_name="resume.pdf")
        setup = handler_test_setup_factory(user_id=6004, document=document)
        setup.context.bot = mock_bot_with_file

        await upload_cv_handler(setup.update, setup.context)

        mock_orchestrator.upload_cv.assert_called_once()
        call_args = mock_orchestrator.upload_cv.call_args
        assert call_args[0][0] == setup.user.id
        assert call_args[0][1].endswith(".pdf")

    async def test_sends_success_message_on_success(
        self, handler_test_setup_factory, mock_bot_with_file, mock_orchestrator
    ):
        """Handler should send success message after successful upload."""
        document = MockDocument(file_name="cv.pdf")
        setup = handler_test_setup_factory(user_id=6005, document=document)
        setup.context.bot = mock_bot_with_file

        await upload_cv_handler(setup.update, setup.context)

        assert messages.SUCCESS_MESSAGE in setup.message._edited_texts

    async def test_handles_validation_error(
        self, handler_test_setup_factory, mock_bot_with_file, mock_orchestrator
    ):
        """Handler should handle validation errors with user-friendly message."""
        document = MockDocument(file_name="cv.pdf")
        setup = handler_test_setup_factory(user_id=6006, document=document)
        setup.context.bot = mock_bot_with_file
        mock_orchestrator.upload_cv.side_effect = ValueError("Invalid PDF format")

        await upload_cv_handler(setup.update, setup.context)

        # Should show generic validation error, not raw exception message
        assert messages.ERROR_VALIDATION_FAILED in setup.message._edited_texts

    async def test_handles_generic_error(
        self, handler_test_setup_factory, mock_bot_with_file, mock_orchestrator
    ):
        """Handler should handle generic errors gracefully."""
        document = MockDocument(file_name="cv.pdf")
        setup = handler_test_setup_factory(user_id=6007, document=document)
        setup.context.bot = mock_bot_with_file
        mock_orchestrator.upload_cv.side_effect = Exception("Unexpected error")

        await upload_cv_handler(setup.update, setup.context)

        assert any(
            messages.ERROR_PROCESSING_FAILED in text for text in setup.message._edited_texts
        )

    async def test_preserves_file_extension(
        self, handler_test_setup_factory, mock_bot_with_file, mock_orchestrator
    ):
        """Handler should preserve the file extension when downloading."""
        document = MockDocument(file_name="my_resume.pdf")
        setup = handler_test_setup_factory(user_id=6008, document=document)
        setup.context.bot = mock_bot_with_file

        await upload_cv_handler(setup.update, setup.context)

        call_args = mock_orchestrator.upload_cv.call_args
        tmp_path = call_args[0][1]
        assert tmp_path.endswith(".pdf")
