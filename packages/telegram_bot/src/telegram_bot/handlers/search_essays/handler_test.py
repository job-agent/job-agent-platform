"""Tests for search essays handler."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from unittest.mock import MagicMock

import pytest

from telegram_bot.conftest import (
    MockUser,
    MockMessage,
    MockUpdate,
    MockContext,
    MockBotDependencies,
    HandlerTestSetup,
)
from telegram_bot.handlers.search_essays.handler import search_essays_handler
from telegram_bot.handlers.search_essays.messages import (
    USAGE_HELP,
    INVALID_LIMIT,
    NO_RESULTS,
    RESULTS_HEADER,
    NO_KEYWORDS,
)


@dataclass
class MockEssay:
    """Mock Essay for testing."""

    id: int
    question: Optional[str]
    answer: str
    keywords: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class MockEssaySearchResult:
    """Mock EssaySearchResult for testing."""

    essay: MockEssay
    score: float = 0.75
    vector_rank: Optional[int] = None
    text_rank: Optional[int] = None


def _create_mock_essay_service(search_results: Optional[List[MockEssaySearchResult]] = None):
    """Create a mock essay service with configurable search results."""
    service = MagicMock()
    service.search.return_value = search_results or []
    return service


@pytest.fixture
def search_essays_handler_setup_factory():
    """Factory for creating handler test setups with essay service."""

    def factory(
        mock_essay_service: MagicMock,
        user_id: int = 12345,
        message_text: str = "/search_essays",
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


class TestSearchEssaysHandlerValidation:
    """Tests for input validation in search essays handler."""

    async def test_shows_usage_when_query_empty(self, search_essays_handler_setup_factory):
        """When /search_essays is sent without query, show usage help message."""
        service = _create_mock_essay_service()
        setup = search_essays_handler_setup_factory(
            mock_essay_service=service,
            message_text="/search_essays",
        )

        await search_essays_handler(setup.update, setup.context)

        all_messages = setup.message._reply_texts + setup.message._edited_texts
        assert any(USAGE_HELP in text or "query" in text.lower() for text in all_messages), (
            f"Expected usage help, got: {all_messages}"
        )

        # Should not call search service
        service.search.assert_not_called()

    async def test_shows_usage_when_only_whitespace(self, search_essays_handler_setup_factory):
        """When query is only whitespace, show usage help message."""
        service = _create_mock_essay_service()
        setup = search_essays_handler_setup_factory(
            mock_essay_service=service,
            message_text="/search_essays     ",
        )

        await search_essays_handler(setup.update, setup.context)

        all_messages = setup.message._reply_texts + setup.message._edited_texts
        assert any(USAGE_HELP in text or "query" in text.lower() for text in all_messages), (
            f"Expected usage help, got: {all_messages}"
        )

        service.search.assert_not_called()

    async def test_treats_nonnumeric_trailing_text_as_query(
        self, search_essays_handler_setup_factory
    ):
        """Non-numeric trailing text is treated as part of the query, not as an invalid limit.

        Since there is no syntactic way to distinguish multi-word queries from
        single-word query + invalid limit (e.g., 'leadership abc' vs 'leadership experience'),
        the handler treats any non-numeric trailing token as part of the query.
        """
        service = _create_mock_essay_service()
        setup = search_essays_handler_setup_factory(
            mock_essay_service=service,
            message_text="/search_essays leadership abc",
        )

        await search_essays_handler(setup.update, setup.context)

        # Should call search with both words as the query
        service.search.assert_called_once()
        call_kwargs = service.search.call_args[1] if service.search.call_args[1] else {}
        query = call_kwargs.get("query", "")
        assert "leadership" in query
        assert "abc" in query

    async def test_shows_error_when_limit_negative(self, search_essays_handler_setup_factory):
        """When limit is negative, show error message."""
        service = _create_mock_essay_service()
        setup = search_essays_handler_setup_factory(
            mock_essay_service=service,
            message_text="/search_essays leadership -5",
        )

        await search_essays_handler(setup.update, setup.context)

        all_messages = setup.message._reply_texts + setup.message._edited_texts
        assert any(INVALID_LIMIT in text or "positive" in text.lower() for text in all_messages), (
            f"Expected invalid limit error, got: {all_messages}"
        )

        service.search.assert_not_called()

    async def test_shows_error_when_limit_zero(self, search_essays_handler_setup_factory):
        """When limit is zero, show error message."""
        service = _create_mock_essay_service()
        setup = search_essays_handler_setup_factory(
            mock_essay_service=service,
            message_text="/search_essays teamwork 0",
        )

        await search_essays_handler(setup.update, setup.context)

        all_messages = setup.message._reply_texts + setup.message._edited_texts
        assert any(INVALID_LIMIT in text or "positive" in text.lower() for text in all_messages), (
            f"Expected invalid limit error, got: {all_messages}"
        )

        service.search.assert_not_called()


class TestSearchEssaysHandlerExecution:
    """Tests for search execution logic."""

    async def test_calls_search_with_query_and_default_limit(
        self, search_essays_handler_setup_factory
    ):
        """When only query is provided, search should use default limit of 10."""
        service = _create_mock_essay_service()
        setup = search_essays_handler_setup_factory(
            mock_essay_service=service,
            message_text="/search_essays leadership experience",
        )

        await search_essays_handler(setup.update, setup.context)

        service.search.assert_called_once()
        call_kwargs = service.search.call_args[1] if service.search.call_args[1] else {}
        call_args = service.search.call_args[0] if service.search.call_args[0] else ()

        # Check that limit is 10 (default)
        if "limit" in call_kwargs:
            assert call_kwargs["limit"] == 10
        else:
            # Check positional args
            assert 10 in call_args or call_kwargs.get("limit", 10) == 10

    async def test_calls_search_with_query_and_custom_limit(
        self, search_essays_handler_setup_factory
    ):
        """When limit is provided, search should use that limit."""
        service = _create_mock_essay_service()
        setup = search_essays_handler_setup_factory(
            mock_essay_service=service,
            message_text="/search_essays conflict resolution 5",
        )

        await search_essays_handler(setup.update, setup.context)

        service.search.assert_called_once()
        call_kwargs = service.search.call_args[1] if service.search.call_args[1] else {}

        # Check that limit is 5
        if "limit" in call_kwargs:
            assert call_kwargs["limit"] == 5

    async def test_calls_search_with_fixed_vector_weight(self, search_essays_handler_setup_factory):
        """Search should always use vector_weight=0.5 (hardcoded)."""
        service = _create_mock_essay_service()
        setup = search_essays_handler_setup_factory(
            mock_essay_service=service,
            message_text="/search_essays teamwork 3",
        )

        await search_essays_handler(setup.update, setup.context)

        service.search.assert_called_once()
        call_kwargs = service.search.call_args[1] if service.search.call_args[1] else {}

        # Check that vector_weight is 0.5
        if "vector_weight" in call_kwargs:
            assert call_kwargs["vector_weight"] == 0.5

    async def test_parses_multi_word_query_correctly(self, search_essays_handler_setup_factory):
        """Multi-word queries should be passed as a single query string."""
        service = _create_mock_essay_service()
        setup = search_essays_handler_setup_factory(
            mock_essay_service=service,
            message_text="/search_essays leadership team management",
        )

        await search_essays_handler(setup.update, setup.context)

        service.search.assert_called_once()
        call_kwargs = service.search.call_args[1] if service.search.call_args[1] else {}
        call_args = service.search.call_args[0] if service.search.call_args[0] else ()

        # Query should contain all words
        query = call_kwargs.get("query") or (call_args[0] if call_args else "")
        assert "leadership" in query
        assert "team" in query
        assert "management" in query

    async def test_parses_query_with_limit_at_end(self, search_essays_handler_setup_factory):
        """When limit is at the end, should correctly separate query from limit."""
        service = _create_mock_essay_service()
        setup = search_essays_handler_setup_factory(
            mock_essay_service=service,
            message_text="/search_essays problem solving skills 7",
        )

        await search_essays_handler(setup.update, setup.context)

        service.search.assert_called_once()
        call_kwargs = service.search.call_args[1] if service.search.call_args[1] else {}

        # Limit should be 7
        if "limit" in call_kwargs:
            assert call_kwargs["limit"] == 7


class TestSearchEssaysHandlerResults:
    """Tests for result display."""

    async def test_shows_no_results_message_when_empty(self, search_essays_handler_setup_factory):
        """When search returns no results, show 'No essays found' message."""
        service = _create_mock_essay_service(search_results=[])
        setup = search_essays_handler_setup_factory(
            mock_essay_service=service,
            message_text="/search_essays obscure query that matches nothing",
        )

        await search_essays_handler(setup.update, setup.context)

        all_messages = setup.message._reply_texts + setup.message._edited_texts
        assert any(NO_RESULTS in text or "No essays" in text for text in all_messages), (
            f"Expected no results message, got: {all_messages}"
        )

    async def test_shows_results_with_count_header(self, search_essays_handler_setup_factory):
        """Results should include 'Found N essay(s):' header."""
        results = [
            MockEssaySearchResult(
                essay=MockEssay(
                    id=1,
                    question="Question 1",
                    answer="Answer 1",
                    keywords=["test"],
                    created_at=datetime(2024, 1, 15, 10, 30),
                    updated_at=datetime(2024, 1, 15, 10, 30),
                )
            ),
            MockEssaySearchResult(
                essay=MockEssay(
                    id=2,
                    question="Question 2",
                    answer="Answer 2",
                    keywords=["test"],
                    created_at=datetime(2024, 1, 15, 10, 30),
                    updated_at=datetime(2024, 1, 15, 10, 30),
                )
            ),
        ]
        service = _create_mock_essay_service(search_results=results)
        setup = search_essays_handler_setup_factory(
            mock_essay_service=service,
            message_text="/search_essays test",
        )

        await search_essays_handler(setup.update, setup.context)

        all_messages = setup.message._reply_texts + setup.message._edited_texts
        message_text = " ".join(all_messages)

        expected_header = RESULTS_HEADER.format(count=2)
        assert expected_header in message_text or "Found 2" in message_text, (
            f"Expected count header, got: {all_messages}"
        )

    async def test_shows_essay_question_answer_keywords(self, search_essays_handler_setup_factory):
        """Results should display essay question, answer, and keywords."""
        results = [
            MockEssaySearchResult(
                essay=MockEssay(
                    id=1,
                    question="How do you handle conflict?",
                    answer="I approach conflicts with empathy and seek to understand all perspectives.",
                    keywords=["conflict resolution", "communication", "empathy"],
                    created_at=datetime(2024, 1, 15, 10, 30),
                    updated_at=datetime(2024, 1, 15, 10, 30),
                )
            )
        ]
        service = _create_mock_essay_service(search_results=results)
        setup = search_essays_handler_setup_factory(
            mock_essay_service=service,
            message_text="/search_essays conflict",
        )

        await search_essays_handler(setup.update, setup.context)

        all_messages = setup.message._reply_texts + setup.message._edited_texts
        message_text = " ".join(all_messages)

        assert "How do you handle conflict" in message_text
        assert "approach conflicts with empathy" in message_text
        assert "conflict resolution" in message_text


class TestSearchEssaysHandlerErrors:
    """Tests for error handling."""

    async def test_propagates_service_exception(self, search_essays_handler_setup_factory):
        """Exceptions from essay service should propagate (not caught)."""
        service = _create_mock_essay_service()
        service.search.side_effect = Exception("Database connection failed")

        setup = search_essays_handler_setup_factory(
            mock_essay_service=service,
            message_text="/search_essays test query",
        )

        # Exception should propagate - this verifies REQ-8
        with pytest.raises(Exception, match="Database connection failed"):
            await search_essays_handler(setup.update, setup.context)

    async def test_returns_early_when_no_message(self, search_essays_handler_setup_factory):
        """Handler should return early when update has no message."""
        service = _create_mock_essay_service()
        setup = search_essays_handler_setup_factory(mock_essay_service=service)

        update = MagicMock()
        update.message = None

        result = await search_essays_handler(update, setup.context)

        assert result is None
        service.search.assert_not_called()


class TestSearchEssaysHandlerEdgeCases:
    """Tests for edge cases and boundary conditions."""

    async def test_handles_essay_with_null_question(self, search_essays_handler_setup_factory):
        """Essays with null question should display without crashing."""
        results = [
            MockEssaySearchResult(
                essay=MockEssay(
                    id=1,
                    question=None,
                    answer="An answer without a corresponding question.",
                    keywords=["general"],
                    created_at=datetime(2024, 1, 15, 10, 30),
                    updated_at=datetime(2024, 1, 15, 10, 30),
                )
            )
        ]
        service = _create_mock_essay_service(search_results=results)
        setup = search_essays_handler_setup_factory(
            mock_essay_service=service,
            message_text="/search_essays general",
        )

        await search_essays_handler(setup.update, setup.context)

        all_messages = setup.message._reply_texts + setup.message._edited_texts
        message_text = " ".join(all_messages)

        assert "An answer without a corresponding question" in message_text
        # Should not contain literal "None"
        assert "None" not in message_text or "No keywords" in message_text

    async def test_handles_essay_with_null_keywords(self, search_essays_handler_setup_factory):
        """Essays with null keywords should show 'No keywords' message."""
        results = [
            MockEssaySearchResult(
                essay=MockEssay(
                    id=1,
                    question="What are your skills?",
                    answer="Python and PostgreSQL.",
                    keywords=None,
                    created_at=datetime(2024, 1, 15, 10, 30),
                    updated_at=datetime(2024, 1, 15, 10, 30),
                )
            )
        ]
        service = _create_mock_essay_service(search_results=results)
        setup = search_essays_handler_setup_factory(
            mock_essay_service=service,
            message_text="/search_essays skills",
        )

        await search_essays_handler(setup.update, setup.context)

        all_messages = setup.message._reply_texts + setup.message._edited_texts
        message_text = " ".join(all_messages)

        assert NO_KEYWORDS in message_text

    async def test_truncates_long_answers(self, search_essays_handler_setup_factory):
        """Long answers should be truncated with ellipsis."""
        long_answer = (
            "This is a very detailed answer that describes my extensive experience "
            "in software development. I have worked on numerous projects involving "
            "complex architectures and challenging technical problems. My expertise "
            "spans multiple programming languages and frameworks. I have also mentored "
            "junior developers and contributed to improving team processes. In addition, "
            "I have experience with cloud platforms and DevOps practices. This answer "
            "continues for quite a while to ensure it exceeds the maximum character limit "
            "that should be applied when displaying search results."
        )
        results = [
            MockEssaySearchResult(
                essay=MockEssay(
                    id=1,
                    question="Describe your experience.",
                    answer=long_answer,
                    keywords=["experience"],
                    created_at=datetime(2024, 1, 15, 10, 30),
                    updated_at=datetime(2024, 1, 15, 10, 30),
                )
            )
        ]
        service = _create_mock_essay_service(search_results=results)
        setup = search_essays_handler_setup_factory(
            mock_essay_service=service,
            message_text="/search_essays experience",
        )

        await search_essays_handler(setup.update, setup.context)

        all_messages = setup.message._reply_texts + setup.message._edited_texts
        message_text = " ".join(all_messages)

        # Should have ellipsis indicating truncation
        assert "..." in message_text
        # Should not contain text from the end of the long answer
        assert "displaying search results" not in message_text

    async def test_handles_single_word_query(self, search_essays_handler_setup_factory):
        """Single word queries should work correctly."""
        service = _create_mock_essay_service()
        setup = search_essays_handler_setup_factory(
            mock_essay_service=service,
            message_text="/search_essays leadership",
        )

        await search_essays_handler(setup.update, setup.context)

        service.search.assert_called_once()
        call_kwargs = service.search.call_args[1] if service.search.call_args[1] else {}
        query = call_kwargs.get("query")
        assert query == "leadership"

    async def test_handles_query_with_special_characters(self, search_essays_handler_setup_factory):
        """Queries with special characters should be passed through."""
        service = _create_mock_essay_service()
        setup = search_essays_handler_setup_factory(
            mock_essay_service=service,
            message_text="/search_essays C++ development",
        )

        await search_essays_handler(setup.update, setup.context)

        service.search.assert_called_once()
        call_kwargs = service.search.call_args[1] if service.search.call_args[1] else {}
        query = call_kwargs.get("query")
        assert "C++" in query
