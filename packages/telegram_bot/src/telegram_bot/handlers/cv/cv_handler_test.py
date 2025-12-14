"""Tests for CV command handler."""

from unittest.mock import MagicMock

import pytest

from telegram_bot.conftest import MockContext, MockMessage, MockUpdate, MockUser
from telegram_bot.di import BotDependencies
from telegram_bot.handlers.cv.handler import cv_handler
from telegram_bot.handlers.cv.messages import CV_SENT_MESSAGE, NO_CV_MESSAGE


@pytest.fixture
def mock_cv_repository():
    """Create a mock CV repository."""
    repo = MagicMock()
    repo.find.return_value = "Test CV content from repository"
    return repo


@pytest.fixture
def mock_dependencies_with_cv(mock_cv_repository):
    """Create mock dependencies with CV repository."""
    orchestrator_factory = MagicMock()
    cv_repository_factory = MagicMock(return_value=mock_cv_repository)

    return BotDependencies(
        orchestrator_factory=orchestrator_factory,
        cv_repository_factory=cv_repository_factory,
    )


@pytest.fixture
def mock_dependencies_without_cv():
    """Create mock dependencies where CV doesn't exist."""
    orchestrator_factory = MagicMock()
    cv_repo = MagicMock()
    cv_repo.find.return_value = None
    cv_repository_factory = MagicMock(return_value=cv_repo)

    return BotDependencies(
        orchestrator_factory=orchestrator_factory,
        cv_repository_factory=cv_repository_factory,
    )


class TestCvHandler:
    """Tests for cv_handler function."""

    async def test_sends_cv_as_document_when_cv_exists(self, mock_dependencies_with_cv):
        """CV handler should send CV as document when CV exists."""
        user = MockUser(id=5001)
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext(dependencies=mock_dependencies_with_cv)

        await cv_handler(update, context)

        assert len(message._reply_documents) == 1
        doc, filename, caption = message._reply_documents[0]
        assert filename == f"cv_{user.id}.txt"
        assert caption == CV_SENT_MESSAGE

    async def test_sends_cv_content_in_document(
        self, mock_dependencies_with_cv, mock_cv_repository
    ):
        """CV handler should include CV content in the document."""
        user = MockUser(id=5002)
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext(dependencies=mock_dependencies_with_cv)

        await cv_handler(update, context)

        doc, _, _ = message._reply_documents[0]
        content = doc.read().decode("utf-8")
        assert content == "Test CV content from repository"

    async def test_sends_no_cv_message_when_cv_not_found(self, mock_dependencies_without_cv):
        """CV handler should send no CV message when CV doesn't exist."""
        user = MockUser(id=5003)
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext(dependencies=mock_dependencies_without_cv)

        await cv_handler(update, context)

        assert len(message._reply_texts) == 1
        assert message._reply_texts[0] == NO_CV_MESSAGE
        assert len(message._reply_documents) == 0

    async def test_creates_cv_repository_for_correct_user(self, mock_dependencies_with_cv):
        """CV handler should create CV repository for the correct user."""
        user = MockUser(id=5004)
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext(dependencies=mock_dependencies_with_cv)

        await cv_handler(update, context)

        mock_dependencies_with_cv.cv_repository_factory.assert_called_once_with(user.id)


class TestCvMessages:
    """Tests for CV message constants."""

    def test_no_cv_message_mentions_upload(self):
        """No CV message should mention uploading a CV."""
        assert "upload" in NO_CV_MESSAGE.lower() or "Upload" in NO_CV_MESSAGE

    def test_cv_sent_message_is_informative(self):
        """CV sent message should be informative."""
        assert len(CV_SENT_MESSAGE) > 0
        assert "CV" in CV_SENT_MESSAGE
