"""Tests for status command handler."""

import pytest

from telegram_bot.conftest import MockContext, MockMessage, MockUpdate, MockUser
from telegram_bot.handlers.status.handler import status_handler
from telegram_bot.handlers.status.messages import (
    ACTIVE_SEARCH_MESSAGE,
    NO_ACTIVE_SEARCH_MESSAGE,
)
from telegram_bot.handlers.state import active_searches


@pytest.fixture(autouse=True)
def clear_active_searches():
    """Clear active_searches before and after each test."""
    active_searches.clear()
    yield
    active_searches.clear()


class TestStatusHandler:
    """Tests for status_handler function."""

    async def test_shows_no_active_search_when_user_has_no_search(self):
        """Status handler should show no active search message when user has no search."""
        user = MockUser(id=1001)
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext()

        await status_handler(update, context)

        assert len(message._reply_texts) == 1
        assert message._reply_texts[0] == NO_ACTIVE_SEARCH_MESSAGE

    async def test_shows_active_search_when_user_has_search(self):
        """Status handler should show active search message when user has active search."""
        user = MockUser(id=1002)
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext()

        active_searches[user.id] = True

        await status_handler(update, context)

        assert len(message._reply_texts) == 1
        assert message._reply_texts[0] == ACTIVE_SEARCH_MESSAGE

    async def test_shows_no_active_search_when_search_is_false(self):
        """Status handler should show no active search when search flag is False."""
        user = MockUser(id=1003)
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext()

        active_searches[user.id] = False

        await status_handler(update, context)

        assert len(message._reply_texts) == 1
        assert message._reply_texts[0] == NO_ACTIVE_SEARCH_MESSAGE

    async def test_does_not_modify_active_searches_state(self):
        """Status handler should not modify the active_searches state."""
        user = MockUser(id=1004)
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext()

        active_searches[user.id] = True

        await status_handler(update, context)

        assert active_searches[user.id] is True

    async def test_different_users_have_independent_status(self):
        """Different users should have independent search status."""
        user1 = MockUser(id=2001)
        user2 = MockUser(id=2002)
        message1 = MockMessage(user=user1)
        message2 = MockMessage(user=user2)
        update1 = MockUpdate(user=user1, message=message1)
        update2 = MockUpdate(user=user2, message=message2)
        context = MockContext()

        active_searches[user1.id] = True

        await status_handler(update1, context)
        await status_handler(update2, context)

        assert message1._reply_texts[0] == ACTIVE_SEARCH_MESSAGE
        assert message2._reply_texts[0] == NO_ACTIVE_SEARCH_MESSAGE


class TestStatusMessages:
    """Tests for status message constants."""

    def test_active_search_message_mentions_cancel(self):
        """Active search message should mention the cancel command."""
        assert "/cancel" in ACTIVE_SEARCH_MESSAGE

    def test_no_active_search_message_mentions_search(self):
        """No active search message should mention the search command."""
        assert "/search" in NO_ACTIVE_SEARCH_MESSAGE
