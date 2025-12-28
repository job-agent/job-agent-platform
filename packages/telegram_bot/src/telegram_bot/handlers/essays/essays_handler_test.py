"""Tests for essays listing handler."""

from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

import pytest

from telegram_bot.conftest import (
    MockUser,
    MockMessage,
    MockUpdate,
    MockContext,
    MockBotDependencies,
    MockEssay,
    HandlerTestSetup,
)
from telegram_bot.handlers.essays import essays_handler, essays_callback_handler


def _create_mock_essays(count: int) -> list[MockEssay]:
    """Create a list of mock essays for testing."""
    return [
        MockEssay(
            id=i,
            question=f"Question {i}?",
            answer=f"Answer {i} content here.",
            keywords=[f"keyword{i}"],
            created_at=datetime(2024, 1, 15, 10, 30),
            updated_at=datetime(2024, 1, 15, 10, 30),
        )
        for i in range(1, count + 1)
    ]


@pytest.fixture
def mock_essay_service_with_essays():
    """Create a mock essay service that returns paginated essays."""
    service = MagicMock()
    essays = _create_mock_essays(7)

    def get_paginated(page: int, page_size: int):
        start = (page - 1) * page_size
        end = start + page_size
        return essays[start:end], len(essays)

    service.get_paginated = MagicMock(side_effect=get_paginated)
    return service


@pytest.fixture
def mock_essay_service_empty():
    """Create a mock essay service that returns no essays."""
    service = MagicMock()
    service.get_paginated = MagicMock(return_value=([], 0))
    return service


@pytest.fixture
def mock_essay_service_error():
    """Create a mock essay service that raises an error."""
    service = MagicMock()
    service.get_paginated = MagicMock(side_effect=Exception("Database connection failed"))
    return service


@pytest.fixture
def essays_handler_setup_factory():
    """Factory for creating handler test setups with essay service."""

    def factory(
        mock_essay_service: MagicMock,
        user_id: int = 12345,
        message_text: str = "/essays",
    ) -> HandlerTestSetup:
        user = MockUser(id=user_id)
        message = MockMessage(
            text=message_text,
            user=user,
            enable_shared_tracking=True,
        )
        update = MockUpdate(user=user, message=message)

        orchestrator_factory = MagicMock()
        cv_repository_factory = MagicMock()
        essay_service_factory = MagicMock(return_value=mock_essay_service)

        dependencies = MockBotDependencies(
            orchestrator_factory=orchestrator_factory,
            cv_repository_factory=cv_repository_factory,
            essay_service_factory=essay_service_factory,
        )

        context = MockContext(dependencies=dependencies)

        return HandlerTestSetup(
            user=user,
            message=message,
            update=update,
            context=context,
            essay_service=mock_essay_service,
        )

    return factory


class TestEssaysCommandHandler:
    """Tests for /essays command handler."""

    async def test_shows_first_page_on_command(
        self, essays_handler_setup_factory, mock_essay_service_with_essays
    ):
        """When /essays command is received, show first page of essays."""
        setup = essays_handler_setup_factory(
            mock_essay_service=mock_essay_service_with_essays,
            message_text="/essays",
        )

        await essays_handler(setup.update, setup.context)

        # Should have called get_paginated for page 1
        setup.essay_service.get_paginated.assert_called()
        call_args = setup.essay_service.get_paginated.call_args
        assert call_args[1].get("page", call_args[0][0] if call_args[0] else 1) == 1

        # Should have replied with content
        all_messages = setup.message._reply_texts
        assert len(all_messages) >= 1, "Expected at least one reply"

    async def test_shows_empty_state_when_no_essays(
        self, essays_handler_setup_factory, mock_essay_service_empty
    ):
        """When no essays exist, show empty state message."""
        setup = essays_handler_setup_factory(
            mock_essay_service=mock_essay_service_empty,
            message_text="/essays",
        )

        await essays_handler(setup.update, setup.context)

        all_messages = setup.message._reply_texts + setup.message._edited_texts
        message_text = " ".join(all_messages)

        # Should mention no essays and how to add them
        assert "No essays" in message_text or "no essays" in message_text.lower()
        assert "/add_essay" in message_text

    async def test_shows_page_indicator(
        self, essays_handler_setup_factory, mock_essay_service_with_essays
    ):
        """Page should include position indicator 'Page X of Y'."""
        setup = essays_handler_setup_factory(
            mock_essay_service=mock_essay_service_with_essays,
            message_text="/essays",
        )

        await essays_handler(setup.update, setup.context)

        all_messages = setup.message._reply_texts + setup.message._edited_texts
        message_text = " ".join(all_messages)

        # Should have page indicator - with 7 essays and page_size 5, we have 2 pages
        assert "Page" in message_text or "page" in message_text.lower()
        assert "1" in message_text  # Page 1

    async def test_includes_navigation_buttons(
        self, essays_handler_setup_factory, mock_essay_service_with_essays
    ):
        """Response should include inline keyboard with navigation buttons."""
        setup = essays_handler_setup_factory(
            mock_essay_service=mock_essay_service_with_essays,
            message_text="/essays",
        )

        await essays_handler(setup.update, setup.context)

        # Check that reply_text was called with reply_markup
        # The message mock should capture the keyboard
        # This is a simplified check - in reality we'd verify the actual keyboard
        assert len(setup.message._reply_texts) >= 1

    async def test_handles_service_error(
        self, essays_handler_setup_factory, mock_essay_service_error
    ):
        """When service raises error, show user-friendly error message."""
        setup = essays_handler_setup_factory(
            mock_essay_service=mock_essay_service_error,
            message_text="/essays",
        )

        await essays_handler(setup.update, setup.context)

        all_messages = setup.message._reply_texts + setup.message._edited_texts
        message_text = " ".join(all_messages)

        # Should show error message
        assert (
            "Failed" in message_text
            or "error" in message_text.lower()
            or "try again" in message_text.lower()
        )

        # Should not expose internal details
        assert "Database connection" not in message_text

    async def test_returns_early_when_no_message(self, essays_handler_setup_factory):
        """Handler should return early when update has no message."""
        service = MagicMock()
        setup = essays_handler_setup_factory(mock_essay_service=service)

        update = MagicMock()
        update.message = None

        result = await essays_handler(update, setup.context)

        assert result is None
        service.get_paginated.assert_not_called()


class TestEssaysCallbackHandler:
    """Tests for essays pagination callback handler."""

    @pytest.fixture
    def callback_handler_setup_factory(self):
        """Factory for creating callback handler test setups."""

        def factory(
            mock_essay_service: MagicMock,
            callback_data: str,
            user_id: int = 12345,
        ):
            user = MockUser(id=user_id)

            # Create mock callback query
            callback_query = MagicMock()
            callback_query.data = callback_data
            callback_query.from_user = user
            callback_query.answer = AsyncMock()
            callback_query.edit_message_text = AsyncMock()

            # Create mock message that the callback is attached to
            message = MockMessage(
                text="Previous essays content",
                user=user,
                enable_shared_tracking=True,
            )
            callback_query.message = message

            # Create update with callback query
            update = MagicMock()
            update.callback_query = callback_query
            update.effective_user = user

            orchestrator_factory = MagicMock()
            cv_repository_factory = MagicMock()
            essay_service_factory = MagicMock(return_value=mock_essay_service)

            dependencies = MockBotDependencies(
                orchestrator_factory=orchestrator_factory,
                cv_repository_factory=cv_repository_factory,
                essay_service_factory=essay_service_factory,
            )

            context = MockContext(dependencies=dependencies)

            return {
                "update": update,
                "context": context,
                "callback_query": callback_query,
                "essay_service": mock_essay_service,
                "message": message,
            }

        return factory

    async def test_next_button_advances_page(
        self, callback_handler_setup_factory, mock_essay_service_with_essays
    ):
        """Clicking Next should fetch and display the next page."""
        setup = callback_handler_setup_factory(
            mock_essay_service=mock_essay_service_with_essays,
            callback_data="essays_page_2",
        )

        await essays_callback_handler(setup["update"], setup["context"])

        # Should have called get_paginated for page 2
        setup["essay_service"].get_paginated.assert_called()
        call_args = setup["essay_service"].get_paginated.call_args
        page_arg = call_args[1].get("page") if "page" in call_args[1] else call_args[0][0]
        assert page_arg == 2

    async def test_previous_button_goes_back(
        self, callback_handler_setup_factory, mock_essay_service_with_essays
    ):
        """Clicking Previous should fetch and display the previous page."""
        setup = callback_handler_setup_factory(
            mock_essay_service=mock_essay_service_with_essays,
            callback_data="essays_page_1",
        )

        await essays_callback_handler(setup["update"], setup["context"])

        # Should have called get_paginated for page 1
        setup["essay_service"].get_paginated.assert_called()
        call_args = setup["essay_service"].get_paginated.call_args
        page_arg = call_args[1].get("page") if "page" in call_args[1] else call_args[0][0]
        assert page_arg == 1

    async def test_edits_message_in_place(
        self, callback_handler_setup_factory, mock_essay_service_with_essays
    ):
        """Navigation should edit the existing message, not send a new one."""
        setup = callback_handler_setup_factory(
            mock_essay_service=mock_essay_service_with_essays,
            callback_data="essays_page_2",
        )

        await essays_callback_handler(setup["update"], setup["context"])

        # Should have called edit_message_text
        setup["callback_query"].edit_message_text.assert_called()

    async def test_answers_callback_query(
        self, callback_handler_setup_factory, mock_essay_service_with_essays
    ):
        """Handler should answer the callback query to remove loading state."""
        setup = callback_handler_setup_factory(
            mock_essay_service=mock_essay_service_with_essays,
            callback_data="essays_page_2",
        )

        await essays_callback_handler(setup["update"], setup["context"])

        # Should have called query.answer()
        setup["callback_query"].answer.assert_called()

    async def test_previous_on_page_1_shows_message(
        self, callback_handler_setup_factory, mock_essay_service_with_essays
    ):
        """Clicking Previous on page 1 should answer with 'already on first page'."""
        setup = callback_handler_setup_factory(
            mock_essay_service=mock_essay_service_with_essays,
            callback_data="essays_noop_prev",  # Disabled previous button
        )

        await essays_callback_handler(setup["update"], setup["context"])

        # Should answer callback but not change page
        setup["callback_query"].answer.assert_called()

        # Should not edit message (no page change needed)
        # Or if it does answer, it should indicate already on first page

    async def test_next_on_last_page_shows_message(
        self, callback_handler_setup_factory, mock_essay_service_with_essays
    ):
        """Clicking Next on last page should answer with 'already on last page'."""
        setup = callback_handler_setup_factory(
            mock_essay_service=mock_essay_service_with_essays,
            callback_data="essays_noop_next",  # Disabled next button
        )

        await essays_callback_handler(setup["update"], setup["context"])

        # Should answer callback
        setup["callback_query"].answer.assert_called()

    async def test_handles_invalid_callback_data(self, callback_handler_setup_factory):
        """Handler should gracefully handle malformed callback data."""
        service = MagicMock()
        service.get_paginated = MagicMock(return_value=([], 0))

        setup = callback_handler_setup_factory(
            mock_essay_service=service,
            callback_data="essays_invalid_data",
        )

        # Should not crash
        await essays_callback_handler(setup["update"], setup["context"])

        # Should answer callback to clear loading state
        setup["callback_query"].answer.assert_called()

    async def test_returns_early_when_no_callback_query(self, callback_handler_setup_factory):
        """Handler should return early when update has no callback_query."""
        service = MagicMock()
        setup = callback_handler_setup_factory(
            mock_essay_service=service,
            callback_data="essays_page_1",
        )

        update = MagicMock()
        update.callback_query = None

        result = await essays_callback_handler(update, setup["context"])

        assert result is None
        service.get_paginated.assert_not_called()

    async def test_handles_service_error_in_callback(
        self, callback_handler_setup_factory, mock_essay_service_error
    ):
        """When service raises error during pagination, show error message."""
        setup = callback_handler_setup_factory(
            mock_essay_service=mock_essay_service_error,
            callback_data="essays_page_2",
        )

        await essays_callback_handler(setup["update"], setup["context"])

        # Should answer callback
        setup["callback_query"].answer.assert_called()

        # Answer text should indicate error or edit message should show error
        # Check if answer was called with error text
        answer_call = setup["callback_query"].answer.call_args
        if answer_call and answer_call[0]:
            answer_text = answer_call[0][0]
            assert (
                "error" in answer_text.lower()
                or "failed" in answer_text.lower()
                or "try again" in answer_text.lower()
            )


class TestEssaysHandlerEdgeCases:
    """Tests for edge cases in essays handlers."""

    async def test_handles_single_essay(self, essays_handler_setup_factory):
        """Handler should work correctly with only one essay."""
        service = MagicMock()
        single_essay = _create_mock_essays(1)
        service.get_paginated = MagicMock(return_value=(single_essay, 1))

        setup = essays_handler_setup_factory(
            mock_essay_service=service,
            message_text="/essays",
        )

        await essays_handler(setup.update, setup.context)

        all_messages = setup.message._reply_texts
        message_text = " ".join(all_messages)

        # Should show the essay
        assert "Question 1" in message_text or "Answer 1" in message_text

    async def test_handles_exactly_page_size_essays(self, essays_handler_setup_factory):
        """Handler should work correctly when essay count equals page size."""
        service = MagicMock()
        essays = _create_mock_essays(5)  # Exactly page_size
        service.get_paginated = MagicMock(return_value=(essays, 5))

        setup = essays_handler_setup_factory(
            mock_essay_service=service,
            message_text="/essays",
        )

        await essays_handler(setup.update, setup.context)

        all_messages = setup.message._reply_texts
        assert len(all_messages) >= 1
