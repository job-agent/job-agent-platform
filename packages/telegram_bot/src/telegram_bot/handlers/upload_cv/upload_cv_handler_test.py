"""Tests for upload CV handler."""

from pathlib import Path
from typing import Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

from telegram_bot.conftest import (
    MockContext,
    MockDocument,
    MockMessage,
    MockUpdate,
    MockUser,
)
from telegram_bot.di import BotDependencies
from telegram_bot.handlers.upload_cv.handler import upload_cv_handler
from telegram_bot.handlers.upload_cv import messages


class MockFile:
    """Mock Telegram File with download capability."""

    def __init__(self, content: bytes = b"PDF content"):
        self.content = content

    async def download_to_drive(self, path: str) -> None:
        """Mock download that creates a file with content."""
        Path(path).write_bytes(self.content)


class TrackingMockMessage:
    """Mock Telegram Message that tracks all edits including on child messages."""

    def __init__(
        self,
        text: str = "",
        document: Optional[MockDocument] = None,
        user: Optional[MockUser] = None,
        tracker: Optional[dict] = None,
    ):
        self.text = text
        self.document = document
        self._user = user or MockUser()
        self._tracker = (
            tracker
            if tracker is not None
            else {
                "reply_texts": [],
                "edited_texts": [],
                "reply_documents": [],
            }
        )

    @property
    def _reply_texts(self):
        return self._tracker["reply_texts"]

    @property
    def _edited_texts(self):
        return self._tracker["edited_texts"]

    @property
    def _reply_documents(self):
        return self._tracker["reply_documents"]

    async def reply_text(self, text: str, **kwargs) -> "TrackingMockMessage":
        """Mock reply_text that records what was sent."""
        self._tracker["reply_texts"].append(text)
        return TrackingMockMessage(text=text, tracker=self._tracker)

    async def reply_document(self, document, filename: str, caption: str = "", **kwargs):
        """Mock reply_document that records what was sent."""
        self._tracker["reply_documents"].append((document, filename, caption))
        return TrackingMockMessage(tracker=self._tracker)

    async def edit_text(self, text: str, **kwargs) -> "TrackingMockMessage":
        """Mock edit_text that records what was edited."""
        self._tracker["edited_texts"].append(text)
        return self


class TrackingMockUpdate:
    """Mock Telegram Update using TrackingMockMessage."""

    def __init__(
        self,
        user: Optional[MockUser] = None,
        message: Optional[TrackingMockMessage] = None,
        document: Optional[MockDocument] = None,
    ):
        self._user = user or MockUser()
        self._message = message or TrackingMockMessage(user=self._user, document=document)

    @property
    def effective_user(self) -> MockUser:
        return self._user

    @property
    def message(self) -> TrackingMockMessage:
        return self._message


@pytest.fixture
def mock_orchestrator():
    """Create a mock orchestrator for upload tests."""
    orchestrator = MagicMock()
    orchestrator.upload_cv.return_value = None
    return orchestrator


@pytest.fixture
def mock_dependencies(mock_orchestrator):
    """Create mock dependencies for upload tests."""
    orchestrator_factory = MagicMock(return_value=mock_orchestrator)
    cv_repository_factory = MagicMock()

    return BotDependencies(
        orchestrator_factory=orchestrator_factory,
        cv_repository_factory=cv_repository_factory,
    )


@pytest.fixture
def mock_bot_with_file():
    """Create a mock bot that returns a mock file."""
    bot = MagicMock()
    bot.get_file = AsyncMock(return_value=MockFile())
    return bot


class TestUploadCvHandler:
    """Tests for upload_cv_handler function."""

    async def test_returns_early_when_no_message(self, mock_dependencies):
        """Handler should return early when update has no message."""
        update = MagicMock()
        update.message = None
        context = MockContext(dependencies=mock_dependencies)

        result = await upload_cv_handler(update, context)

        assert result is None

    async def test_returns_early_when_no_document(self, mock_dependencies):
        """Handler should return early when message has no document."""
        user = MockUser(id=6001)
        message = MockMessage(user=user, document=None)
        update = MockUpdate(user=user, message=message)
        context = MockContext(dependencies=mock_dependencies)

        result = await upload_cv_handler(update, context)

        assert result is None

    async def test_sends_processing_message(
        self, mock_dependencies, mock_bot_with_file, mock_orchestrator
    ):
        """Handler should send processing message first."""
        user = MockUser(id=6002)
        document = MockDocument(file_name="test.pdf")
        message = TrackingMockMessage(user=user, document=document)
        update = TrackingMockUpdate(user=user, message=message, document=document)
        context = MockContext(dependencies=mock_dependencies)
        context.bot = mock_bot_with_file

        await upload_cv_handler(update, context)

        assert messages.INFO_PROCESSING in message._reply_texts

    async def test_downloads_file_from_telegram(
        self, mock_dependencies, mock_bot_with_file, mock_orchestrator
    ):
        """Handler should download the file from Telegram."""
        user = MockUser(id=6003)
        document = MockDocument(file_id="test_file_123", file_name="cv.pdf")
        message = TrackingMockMessage(user=user, document=document)
        update = TrackingMockUpdate(user=user, message=message, document=document)
        context = MockContext(dependencies=mock_dependencies)
        context.bot = mock_bot_with_file

        await upload_cv_handler(update, context)

        mock_bot_with_file.get_file.assert_called_once_with(document.file_id)

    async def test_calls_orchestrator_upload_cv(
        self, mock_dependencies, mock_bot_with_file, mock_orchestrator
    ):
        """Handler should call orchestrator.upload_cv with correct arguments."""
        user = MockUser(id=6004)
        document = MockDocument(file_name="resume.pdf")
        message = TrackingMockMessage(user=user, document=document)
        update = TrackingMockUpdate(user=user, message=message, document=document)
        context = MockContext(dependencies=mock_dependencies)
        context.bot = mock_bot_with_file

        await upload_cv_handler(update, context)

        mock_orchestrator.upload_cv.assert_called_once()
        call_args = mock_orchestrator.upload_cv.call_args
        assert call_args[0][0] == user.id
        assert call_args[0][1].endswith(".pdf")

    async def test_sends_success_message_on_success(
        self, mock_dependencies, mock_bot_with_file, mock_orchestrator
    ):
        """Handler should send success message after successful upload."""
        user = MockUser(id=6005)
        document = MockDocument(file_name="cv.pdf")
        message = TrackingMockMessage(user=user, document=document)
        update = TrackingMockUpdate(user=user, message=message, document=document)
        context = MockContext(dependencies=mock_dependencies)
        context.bot = mock_bot_with_file

        await upload_cv_handler(update, context)

        assert messages.SUCCESS_MESSAGE in message._edited_texts

    async def test_handles_validation_error(
        self, mock_dependencies, mock_bot_with_file, mock_orchestrator
    ):
        """Handler should handle validation errors from orchestrator."""
        user = MockUser(id=6006)
        document = MockDocument(file_name="cv.pdf")
        message = TrackingMockMessage(user=user, document=document)
        update = TrackingMockUpdate(user=user, message=message, document=document)
        context = MockContext(dependencies=mock_dependencies)
        context.bot = mock_bot_with_file

        mock_orchestrator.upload_cv.side_effect = ValueError("Invalid PDF format")

        await upload_cv_handler(update, context)

        assert any("Invalid PDF format" in text for text in message._edited_texts)

    async def test_handles_generic_error(
        self, mock_dependencies, mock_bot_with_file, mock_orchestrator
    ):
        """Handler should handle generic errors gracefully."""
        user = MockUser(id=6007)
        document = MockDocument(file_name="cv.pdf")
        message = TrackingMockMessage(user=user, document=document)
        update = TrackingMockUpdate(user=user, message=message, document=document)
        context = MockContext(dependencies=mock_dependencies)
        context.bot = mock_bot_with_file

        mock_orchestrator.upload_cv.side_effect = Exception("Unexpected error")

        await upload_cv_handler(update, context)

        assert any(messages.ERROR_PROCESSING_FAILED in text for text in message._edited_texts)

    async def test_preserves_file_extension(
        self, mock_dependencies, mock_bot_with_file, mock_orchestrator
    ):
        """Handler should preserve the file extension when downloading."""
        user = MockUser(id=6008)
        document = MockDocument(file_name="my_resume.pdf")
        message = TrackingMockMessage(user=user, document=document)
        update = TrackingMockUpdate(user=user, message=message, document=document)
        context = MockContext(dependencies=mock_dependencies)
        context.bot = mock_bot_with_file

        await upload_cv_handler(update, context)

        call_args = mock_orchestrator.upload_cv.call_args
        tmp_path = call_args[0][1]
        assert tmp_path.endswith(".pdf")


class TestUploadCvMessages:
    """Tests for upload CV message constants."""

    def test_success_message_indicates_success(self):
        """Success message should indicate successful upload."""
        assert "success" in messages.SUCCESS_MESSAGE.lower()
        assert "CV" in messages.SUCCESS_MESSAGE

    def test_success_message_mentions_search(self):
        """Success message should mention the search command."""
        assert "/search" in messages.SUCCESS_MESSAGE

    def test_error_message_indicates_failure(self):
        """Error message should indicate processing failure."""
        assert (
            "Failed" in messages.ERROR_PROCESSING_FAILED
            or "error" in messages.ERROR_PROCESSING_FAILED.lower()
        )

    def test_info_processing_indicates_processing(self):
        """Info processing message should indicate processing."""
        assert (
            "Processing" in messages.INFO_PROCESSING
            or "processing" in messages.INFO_PROCESSING.lower()
        )
