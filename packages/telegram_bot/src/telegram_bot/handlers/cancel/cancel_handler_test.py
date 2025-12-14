"""Tests for cancel command handler."""

import pytest

from telegram_bot.conftest import MockContext, MockMessage, MockUpdate, MockUser
from telegram_bot.handlers.cancel.handler import cancel_handler
from telegram_bot.handlers.cancel.messages import (
    CANCELLING_MESSAGE,
    NO_SEARCH_TO_CANCEL_MESSAGE,
)
from telegram_bot.handlers.state import active_searches


@pytest.fixture(autouse=True)
def clear_active_searches():
    """Clear active_searches before and after each test."""
    active_searches.clear()
    yield
    active_searches.clear()


class TestCancelHandler:
    """Tests for cancel_handler function."""

    async def test_shows_no_search_to_cancel_when_no_active_search(self):
        """Cancel handler should show message when user has no active search."""
        user = MockUser(id=3001)
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext()

        await cancel_handler(update, context)

        assert len(message._reply_texts) == 1
        assert message._reply_texts[0] == NO_SEARCH_TO_CANCEL_MESSAGE

    async def test_cancels_active_search(self):
        """Cancel handler should cancel an active search."""
        user = MockUser(id=3002)
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext()

        active_searches[user.id] = True

        await cancel_handler(update, context)

        assert len(message._reply_texts) == 1
        assert message._reply_texts[0] == CANCELLING_MESSAGE
        assert active_searches[user.id] is False

    async def test_shows_no_search_when_search_is_false(self):
        """Cancel handler should show no search message when flag is False."""
        user = MockUser(id=3003)
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext()

        active_searches[user.id] = False

        await cancel_handler(update, context)

        assert len(message._reply_texts) == 1
        assert message._reply_texts[0] == NO_SEARCH_TO_CANCEL_MESSAGE

    async def test_sets_search_flag_to_false(self):
        """Cancel handler should set the search flag to False."""
        user = MockUser(id=3004)
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext()

        active_searches[user.id] = True

        await cancel_handler(update, context)

        assert active_searches[user.id] is False

    async def test_does_not_affect_other_users(self):
        """Cancelling one user's search should not affect other users."""
        user1 = MockUser(id=4001)
        user2 = MockUser(id=4002)
        message1 = MockMessage(user=user1)
        update1 = MockUpdate(user=user1, message=message1)
        context = MockContext()

        active_searches[user1.id] = True
        active_searches[user2.id] = True

        await cancel_handler(update1, context)

        assert active_searches[user1.id] is False
        assert active_searches[user2.id] is True


class TestCancelMessages:
    """Tests for cancel message constants."""

    def test_cancelling_message_indicates_stopping(self):
        """Cancelling message should indicate the search is being stopped."""
        assert "Cancelling" in CANCELLING_MESSAGE or "cancel" in CANCELLING_MESSAGE.lower()

    def test_no_search_message_mentions_search_command(self):
        """No search to cancel message should mention the search command."""
        assert "/search" in NO_SEARCH_TO_CANCEL_MESSAGE
