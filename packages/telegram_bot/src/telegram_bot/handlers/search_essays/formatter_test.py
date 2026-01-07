"""Tests for search essays formatter functions."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import pytest

from telegram_bot.handlers.search_essays.formatter import (
    format_search_result_item,
    format_search_results,
    ANSWER_MAX_LENGTH,
)
from telegram_bot.handlers.search_essays.messages import NO_RESULTS, RESULTS_HEADER, NO_KEYWORDS


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


class TestFormatSearchResultItem:
    """Tests for format_search_result_item function."""

    @pytest.fixture
    def result_with_all_fields(self):
        """Create a search result with all fields populated."""
        essay = MockEssay(
            id=1,
            question="Tell me about a time you demonstrated leadership.",
            answer="I led a cross-functional team of 10 engineers during a critical product launch.",
            keywords=["leadership", "teamwork", "project management"],
            created_at=datetime(2024, 1, 15, 10, 30),
            updated_at=datetime(2024, 1, 15, 10, 30),
        )
        return MockEssaySearchResult(essay=essay, score=0.85, vector_rank=1, text_rank=2)

    @pytest.fixture
    def result_without_question(self):
        """Create a search result where essay has no question."""
        essay = MockEssay(
            id=2,
            question=None,
            answer="A standalone answer without a corresponding question.",
            keywords=["general"],
            created_at=datetime(2024, 1, 15, 10, 30),
            updated_at=datetime(2024, 1, 15, 10, 30),
        )
        return MockEssaySearchResult(essay=essay)

    @pytest.fixture
    def result_without_keywords(self):
        """Create a search result where essay has no keywords."""
        essay = MockEssay(
            id=3,
            question="What are your technical skills?",
            answer="Python, Django, PostgreSQL, and Docker.",
            keywords=None,
            created_at=datetime(2024, 1, 15, 10, 30),
            updated_at=datetime(2024, 1, 15, 10, 30),
        )
        return MockEssaySearchResult(essay=essay)

    @pytest.fixture
    def result_with_long_answer(self):
        """Create a search result with answer exceeding max length."""
        long_answer = (
            "This is a very detailed answer that describes my extensive experience "
            "in software development. I have worked on numerous projects involving "
            "complex architectures and challenging technical problems. My expertise "
            "spans multiple programming languages and frameworks. I have also mentored "
            "junior developers and contributed to improving team processes. In addition, "
            "I have experience with cloud platforms and DevOps practices. This answer "
            "continues for quite a while to ensure it exceeds the maximum character limit."
        )
        essay = MockEssay(
            id=4,
            question="Describe your experience.",
            answer=long_answer,
            keywords=["experience", "software development"],
            created_at=datetime(2024, 1, 15, 10, 30),
            updated_at=datetime(2024, 1, 15, 10, 30),
        )
        return MockEssaySearchResult(essay=essay)

    def test_shows_question_field(self, result_with_all_fields):
        """When essay has a question, formatted output should include Question label."""
        formatted = format_search_result_item(result_with_all_fields)

        assert "Question:" in formatted
        assert "Tell me about a time you demonstrated leadership" in formatted

    def test_shows_answer_field(self, result_with_all_fields):
        """Formatted output should include Answer label and content."""
        formatted = format_search_result_item(result_with_all_fields)

        assert "Answer:" in formatted
        assert "led a cross-functional team" in formatted

    def test_shows_keywords_comma_separated(self, result_with_all_fields):
        """When essay has keywords, they should be displayed comma-separated."""
        formatted = format_search_result_item(result_with_all_fields)

        assert "Keywords:" in formatted
        assert "leadership" in formatted
        assert "teamwork" in formatted
        assert "project management" in formatted

    def test_handles_missing_question(self, result_without_question):
        """When question is None, should not crash and should not show Question label."""
        formatted = format_search_result_item(result_without_question)

        assert "A standalone answer" in formatted
        # Should not show "None" literally
        assert "None" not in formatted
        # Question label should be absent or have no content
        assert "Question:" not in formatted or "Question: \n" in formatted

    def test_handles_missing_keywords(self, result_without_keywords):
        """When keywords is None, should show 'No keywords' message."""
        formatted = format_search_result_item(result_without_keywords)

        assert "Python, Django" in formatted
        assert NO_KEYWORDS in formatted

    def test_truncates_long_answer_with_ellipsis(self, result_with_long_answer):
        """Answers exceeding max length should be truncated with '...'."""
        formatted = format_search_result_item(result_with_long_answer)

        # Should have ellipsis
        assert "..." in formatted
        # Should not contain text from the end of the long answer
        assert "exceeds the maximum character limit" not in formatted

    def test_truncated_answer_respects_max_length(self, result_with_long_answer):
        """Answer portion should not exceed ANSWER_MAX_LENGTH plus ellipsis."""
        formatted = format_search_result_item(result_with_long_answer)

        # Find the answer content (between Answer: and Keywords:)
        answer_start = formatted.find("Answer:")
        answer_end = formatted.find("Keywords:")
        if answer_end == -1:
            answer_end = len(formatted)

        answer_section = formatted[answer_start:answer_end]

        # The answer section should be reasonably bounded
        # (label + truncated content + some formatting)
        assert len(answer_section) < ANSWER_MAX_LENGTH + 100

    def test_handles_empty_keywords_list(self):
        """When keywords is an empty list, should show 'No keywords'."""
        essay = MockEssay(
            id=5,
            question="A question",
            answer="An answer",
            keywords=[],
            created_at=datetime(2024, 1, 15, 10, 30),
            updated_at=datetime(2024, 1, 15, 10, 30),
        )
        result = MockEssaySearchResult(essay=essay)

        formatted = format_search_result_item(result)

        assert NO_KEYWORDS in formatted


class TestFormatSearchResults:
    """Tests for format_search_results function."""

    @pytest.fixture
    def sample_results(self):
        """Create a list of sample search results."""
        results = []
        for i in range(1, 4):
            essay = MockEssay(
                id=i,
                question=f"Question {i}?",
                answer=f"Answer {i} content here.",
                keywords=[f"keyword{i}"],
                created_at=datetime(2024, 1, 15, 10, 30),
                updated_at=datetime(2024, 1, 15, 10, 30),
            )
            results.append(MockEssaySearchResult(essay=essay, score=0.9 - i * 0.1))
        return results

    def test_shows_count_header(self, sample_results):
        """Results should include header with count of essays found."""
        formatted = format_search_results(sample_results)

        expected_header = RESULTS_HEADER.format(count=3)
        assert expected_header in formatted

    def test_includes_all_essays(self, sample_results):
        """Formatted output should include all provided essays."""
        formatted = format_search_results(sample_results)

        assert "Question 1?" in formatted
        assert "Answer 1 content" in formatted
        assert "Question 2?" in formatted
        assert "Answer 2 content" in formatted
        assert "Question 3?" in formatted
        assert "Answer 3 content" in formatted

    def test_separates_essays_with_divider(self, sample_results):
        """Essays should be separated by visual dividers."""
        formatted = format_search_results(sample_results)

        # Should have separators between essays (at least 2 for 3 essays)
        # Using newline-based separation
        assert formatted.count("---") >= 2 or formatted.count("\n\n") >= 2

    def test_returns_no_results_message_when_empty(self):
        """When results list is empty, should return 'No essays found' message."""
        formatted = format_search_results([])

        assert NO_RESULTS in formatted

    def test_single_result_has_header(self):
        """Even single result should have count header."""
        essay = MockEssay(
            id=1,
            question="Single question",
            answer="Single answer",
            keywords=["single"],
            created_at=datetime(2024, 1, 15, 10, 30),
            updated_at=datetime(2024, 1, 15, 10, 30),
        )
        result = MockEssaySearchResult(essay=essay)

        formatted = format_search_results([result])

        expected_header = RESULTS_HEADER.format(count=1)
        assert expected_header in formatted


class TestFormatterWithNullFields:
    """Tests for handling various null/None field combinations."""

    def test_result_with_only_answer(self):
        """Essay with only answer (no question, no keywords) should format correctly."""
        essay = MockEssay(
            id=1,
            question=None,
            answer="This is the only content.",
            keywords=None,
            created_at=datetime(2024, 1, 15, 10, 30),
            updated_at=datetime(2024, 1, 15, 10, 30),
        )
        result = MockEssaySearchResult(essay=essay)

        formatted = format_search_result_item(result)

        assert "This is the only content" in formatted
        assert NO_KEYWORDS in formatted

    def test_result_with_empty_question_string(self):
        """Essay with empty string question should be treated like None."""
        essay = MockEssay(
            id=1,
            question="",
            answer="Answer with empty question.",
            keywords=["test"],
            created_at=datetime(2024, 1, 15, 10, 30),
            updated_at=datetime(2024, 1, 15, 10, 30),
        )
        result = MockEssaySearchResult(essay=essay)

        formatted = format_search_result_item(result)

        # Should not show empty question
        assert "Answer with empty question" in formatted
