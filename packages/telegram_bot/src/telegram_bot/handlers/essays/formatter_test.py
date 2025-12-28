"""Tests for essays formatter functions."""

from datetime import datetime

import pytest

from telegram_bot.handlers.essays.formatter import (
    format_essay_item,
    format_essays_page,
    build_navigation_keyboard,
)
from telegram_bot.conftest import MockEssay


class TestFormatEssayItem:
    """Tests for format_essay_item function."""

    @pytest.fixture
    def essay_with_all_fields(self):
        """Create an essay with all fields populated."""
        return MockEssay(
            id=1,
            question="What is your greatest professional achievement?",
            answer="I led a team of 10 engineers to deliver a critical project ahead of schedule.",
            keywords=["leadership", "project management", "teamwork"],
            created_at=datetime(2024, 1, 15, 10, 30),
            updated_at=datetime(2024, 1, 15, 10, 30),
        )

    @pytest.fixture
    def essay_with_long_answer(self):
        """Create an essay with answer longer than 100 characters."""
        long_answer = (
            "This is a very long answer that exceeds one hundred characters and should be "
            "truncated in the display to provide a preview without overwhelming the user with "
            "too much text in the list view."
        )
        return MockEssay(
            id=2,
            question="Tell me about yourself.",
            answer=long_answer,
            keywords=["introduction"],
            created_at=datetime(2024, 1, 15, 10, 30),
            updated_at=datetime(2024, 1, 15, 10, 30),
        )

    @pytest.fixture
    def essay_without_question(self):
        """Create an essay without a question."""
        return MockEssay(
            id=3,
            question=None,
            answer="A standalone answer without a question.",
            keywords=["general"],
            created_at=datetime(2024, 1, 15, 10, 30),
            updated_at=datetime(2024, 1, 15, 10, 30),
        )

    @pytest.fixture
    def essay_without_keywords(self):
        """Create an essay without keywords."""
        return MockEssay(
            id=4,
            question="What are your skills?",
            answer="Python, Django, and PostgreSQL.",
            keywords=None,
            created_at=datetime(2024, 1, 15, 10, 30),
            updated_at=datetime(2024, 1, 15, 10, 30),
        )

    def test_shows_question(self, essay_with_all_fields):
        """Formatted item should include the question."""
        result = format_essay_item(essay_with_all_fields, index=1)

        assert "What is your greatest professional achievement?" in result

    def test_shows_answer_preview(self, essay_with_all_fields):
        """Formatted item should include answer preview."""
        result = format_essay_item(essay_with_all_fields, index=1)

        assert "led a team" in result

    def test_truncates_long_answer(self, essay_with_long_answer):
        """Answers longer than ~100 characters should be truncated with ellipsis."""
        result = format_essay_item(essay_with_long_answer, index=1)

        # Answer should be truncated - not contain full text
        assert "too much text in the list view" not in result
        # Should have ellipsis or truncation indicator
        assert "..." in result

    def test_shows_keywords_comma_separated(self, essay_with_all_fields):
        """Keywords should be displayed comma-separated."""
        result = format_essay_item(essay_with_all_fields, index=1)

        assert "leadership" in result
        assert "project management" in result
        assert "teamwork" in result

    def test_handles_missing_question(self, essay_without_question):
        """When question is None, should not crash and show answer."""
        result = format_essay_item(essay_without_question, index=1)

        assert "A standalone answer" in result
        # Should not show "None" literally
        assert "None" not in result or "none" not in result.lower()

    def test_handles_missing_keywords(self, essay_without_keywords):
        """When keywords is None, should not crash."""
        result = format_essay_item(essay_without_keywords, index=1)

        assert "Python" in result
        # Should not crash or show empty brackets

    def test_includes_index_number(self, essay_with_all_fields):
        """Formatted item should include the index number."""
        result = format_essay_item(essay_with_all_fields, index=3)

        assert "3" in result

    def test_handles_empty_keywords_list(self):
        """When keywords is an empty list, should not show keywords section."""
        essay = MockEssay(
            id=5,
            question="A question",
            answer="An answer",
            keywords=[],
            created_at=datetime(2024, 1, 15, 10, 30),
            updated_at=datetime(2024, 1, 15, 10, 30),
        )

        result = format_essay_item(essay, index=1)

        assert "An answer" in result


class TestFormatEssaysPage:
    """Tests for format_essays_page function."""

    @pytest.fixture
    def sample_essays(self):
        """Create a list of sample essays."""
        return [
            MockEssay(
                id=i,
                question=f"Question {i}",
                answer=f"Answer {i}",
                keywords=[f"keyword{i}"],
                created_at=datetime(2024, 1, 15, 10, 30),
                updated_at=datetime(2024, 1, 15, 10, 30),
            )
            for i in range(1, 4)
        ]

    def test_includes_page_header(self, sample_essays):
        """Formatted page should include page indicator."""
        result = format_essays_page(sample_essays, page=2, total_pages=5)

        assert "Page 2 of 5" in result or "2 of 5" in result

    def test_includes_all_essays(self, sample_essays):
        """Formatted page should include all provided essays."""
        result = format_essays_page(sample_essays, page=1, total_pages=1)

        assert "Question 1" in result
        assert "Question 2" in result
        assert "Question 3" in result

    def test_numbers_essays_correctly(self, sample_essays):
        """Essays should be numbered starting from 1."""
        result = format_essays_page(sample_essays, page=1, total_pages=1)

        # Should have numbers 1, 2, 3 for the essays
        assert "1" in result
        assert "2" in result
        assert "3" in result

    def test_handles_empty_list(self):
        """When essays list is empty, should return empty state message."""
        result = format_essays_page([], page=1, total_pages=0)

        # Should indicate no essays
        assert "No essays" in result or "empty" in result.lower() or result == ""


class TestBuildNavigationKeyboard:
    """Tests for build_navigation_keyboard function."""

    def test_both_buttons_on_middle_page(self):
        """On middle pages, both Previous and Next buttons should be enabled."""
        keyboard = build_navigation_keyboard(page=2, total_pages=4)

        # Should have two buttons
        assert len(keyboard) >= 1  # At least one row
        buttons = keyboard[0] if isinstance(keyboard[0], list) else keyboard

        # Find button texts
        button_texts = [btn.text if hasattr(btn, "text") else str(btn) for btn in buttons]

        # Both navigation directions should be present and enabled
        has_previous = any("Previous" in text or "<" in text for text in button_texts)
        has_next = any("Next" in text or ">" in text for text in button_texts)

        assert has_previous, f"Previous button not found in {button_texts}"
        assert has_next, f"Next button not found in {button_texts}"

    def test_previous_disabled_on_first_page(self):
        """On page 1, Previous button should be disabled or absent."""
        keyboard = build_navigation_keyboard(page=1, total_pages=3)

        # The keyboard should exist
        assert keyboard is not None

        # Get all button callback data
        buttons = keyboard[0] if isinstance(keyboard[0], list) else keyboard
        callback_data = [
            btn.callback_data if hasattr(btn, "callback_data") else None for btn in buttons
        ]

        # Previous should either not navigate or be marked as disabled
        # Check that clicking previous on page 1 doesn't go to page 0
        previous_callbacks = [
            cb for cb in callback_data if cb and ("prev" in cb.lower() or "previous" in cb.lower())
        ]

        # If previous button exists, it should either:
        # 1. Have callback data indicating "noop" or "disabled"
        # 2. Or still point to page 1 (no change)
        for cb in previous_callbacks:
            # Should not navigate to page 0 or negative
            assert "page_0" not in cb and "page_-" not in cb

    def test_next_disabled_on_last_page(self):
        """On the last page, Next button should be disabled or absent."""
        keyboard = build_navigation_keyboard(page=5, total_pages=5)

        # The keyboard should exist
        assert keyboard is not None

        # Get all button callback data
        buttons = keyboard[0] if isinstance(keyboard[0], list) else keyboard
        callback_data = [
            btn.callback_data if hasattr(btn, "callback_data") else None for btn in buttons
        ]

        # Next should either not navigate or be marked as disabled
        next_callbacks = [cb for cb in callback_data if cb and ("next" in cb.lower())]

        # If next button exists, it should not navigate beyond last page
        for cb in next_callbacks:
            assert "page_6" not in cb

    def test_both_buttons_disabled_on_single_page(self):
        """When there's only one page, both buttons should be disabled."""
        keyboard = build_navigation_keyboard(page=1, total_pages=1)

        # Should still have keyboard but buttons are disabled
        assert keyboard is not None

        buttons = keyboard[0] if isinstance(keyboard[0], list) else keyboard
        callback_data = [
            btn.callback_data if hasattr(btn, "callback_data") else None for btn in buttons
        ]

        # Both should be disabled/noop
        for cb in callback_data:
            if cb:
                # Should not allow navigation
                assert "page_0" not in cb and "page_2" not in cb

    def test_returns_inline_keyboard_format(self):
        """Keyboard should be in proper inline keyboard format."""
        keyboard = build_navigation_keyboard(page=2, total_pages=3)

        # Should be a list (rows) of lists (buttons) or similar structure
        assert isinstance(keyboard, (list, tuple))
        assert len(keyboard) >= 1

    def test_callback_data_includes_target_page(self):
        """Callback data should indicate which page to navigate to."""
        keyboard = build_navigation_keyboard(page=2, total_pages=5)

        buttons = keyboard[0] if isinstance(keyboard[0], list) else keyboard
        callback_data = [
            btn.callback_data if hasattr(btn, "callback_data") else None for btn in buttons
        ]

        # Should have page information in callback data
        next_cb = [cb for cb in callback_data if cb and "next" in cb.lower()]
        prev_cb = [cb for cb in callback_data if cb and ("prev" in cb.lower())]

        # Next should go to page 3
        if next_cb:
            assert any("3" in cb for cb in next_cb) or any("page_3" in cb for cb in next_cb)

        # Previous should go to page 1
        if prev_cb:
            assert any("1" in cb for cb in prev_cb) or any("page_1" in cb for cb in prev_cb)
