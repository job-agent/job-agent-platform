"""Tests for search command handler."""

import pytest

from telegram_bot.conftest import MockUser
from telegram_bot.handlers.search.handler import search_jobs_handler
from telegram_bot.handlers.state import active_searches


@pytest.fixture(autouse=True)
def clear_active_searches():
    """Clear active_searches before and after each test."""
    active_searches.clear()
    yield
    active_searches.clear()


class TestSearchHandlerParameterParsing:
    """Tests for parameter parsing in search handler."""

    async def test_uses_default_parameters_when_no_args(self, handler_test_setup_factory):
        """Handler should use default parameters when no args provided."""
        setup = handler_test_setup_factory(user_id=7001, args=[])

        await search_jobs_handler(setup.update, setup.context)

        assert any("4000" in text for text in setup.message._reply_texts)
        assert any("remote" in text.lower() for text in setup.message._reply_texts)

    async def test_parses_min_salary_parameter(self, handler_test_setup_factory):
        """Handler should parse min_salary parameter."""
        setup = handler_test_setup_factory(user_id=7002, args=["min_salary=5000"])

        await search_jobs_handler(setup.update, setup.context)

        assert any("5000" in text for text in setup.message._reply_texts)

    async def test_parses_employment_location_parameter(self, handler_test_setup_factory):
        """Handler should parse employment_location parameter."""
        setup = handler_test_setup_factory(user_id=7003, args=["employment_location=hybrid"])

        await search_jobs_handler(setup.update, setup.context)

        assert any("hybrid" in text.lower() for text in setup.message._reply_texts)

    async def test_parses_days_parameter(self, handler_test_setup_factory):
        """Handler should parse days parameter."""
        setup = handler_test_setup_factory(user_id=7004, args=["days=7"])

        await search_jobs_handler(setup.update, setup.context)

        assert any("7 days" in text or "Last 7" in text for text in setup.message._reply_texts)

    async def test_rejects_deprecated_salary_parameter(self, handler_test_setup_factory):
        """Handler should reject the deprecated 'salary' parameter."""
        setup = handler_test_setup_factory(user_id=7005, args=["salary=5000"])

        await search_jobs_handler(setup.update, setup.context)

        assert any("no longer supported" in text.lower() for text in setup.message._reply_texts)
        assert any("min_salary" in text for text in setup.message._reply_texts)

    async def test_rejects_invalid_numeric_parameter(self, handler_test_setup_factory):
        """Handler should reject invalid numeric parameter values."""
        setup = handler_test_setup_factory(user_id=7006, args=["min_salary=invalid"])

        await search_jobs_handler(setup.update, setup.context)

        assert any("Invalid value" in text for text in setup.message._reply_texts)

    async def test_parses_multiple_parameters(self, handler_test_setup_factory):
        """Handler should parse multiple parameters."""
        setup = handler_test_setup_factory(
            user_id=7007,
            args=["min_salary=6000", "employment_location=onsite", "days=3"],
        )

        await search_jobs_handler(setup.update, setup.context)

        params_message = setup.message._reply_texts[0]
        assert "6000" in params_message
        assert "onsite" in params_message.lower()
        assert "3" in params_message


class TestSearchHandlerCvValidation:
    """Tests for CV validation in search handler."""

    async def test_requires_cv_before_search(self, handler_test_setup_factory, mock_orchestrator):
        """Handler should require CV to be uploaded before searching."""
        mock_orchestrator.has_cv.return_value = False
        setup = handler_test_setup_factory(user_id=7101)

        await search_jobs_handler(setup.update, setup.context)

        assert any("No CV found" in text for text in setup.message._reply_texts)
        assert any("upload" in text.lower() for text in setup.message._reply_texts)

    async def test_proceeds_when_cv_exists(self, handler_test_setup_factory, mock_orchestrator):
        """Handler should proceed when CV exists."""
        # mock_orchestrator defaults to has_cv=True
        setup = handler_test_setup_factory(user_id=7102)

        await search_jobs_handler(setup.update, setup.context)

        assert any("Starting job search" in text for text in setup.message._reply_texts)


class TestSearchHandlerConcurrency:
    """Tests for concurrent search prevention."""

    async def test_prevents_concurrent_searches(self, handler_test_setup_factory):
        """Handler should prevent concurrent searches for same user."""
        setup = handler_test_setup_factory(user_id=7201)
        active_searches[setup.user.id] = True

        await search_jobs_handler(setup.update, setup.context)

        assert any(
            "already have a search running" in text.lower() for text in setup.message._reply_texts
        )

    async def test_allows_different_users_to_search(self, handler_test_setup_factory):
        """Handler should allow different users to search concurrently."""
        user1 = MockUser(id=7202)
        active_searches[user1.id] = True

        setup = handler_test_setup_factory(user_id=7203)

        await search_jobs_handler(setup.update, setup.context)

        assert not any(
            "already have a search running" in text.lower() for text in setup.message._reply_texts
        )


class TestSearchHandlerStateManagement:
    """Tests for active search state management."""

    async def test_sets_active_search_at_start(self, handler_test_setup_factory, mock_orchestrator):
        """Handler should set active_searches to True at start."""
        # mock_orchestrator defaults to has_cv=True
        setup = handler_test_setup_factory(user_id=7301)

        await search_jobs_handler(setup.update, setup.context)

        assert active_searches.get(setup.user.id) is False

    async def test_clears_active_search_on_completion(
        self, handler_test_setup_factory, mock_orchestrator
    ):
        """Handler should clear active_searches on completion."""
        # mock_orchestrator defaults to has_cv=True
        setup = handler_test_setup_factory(user_id=7302)

        await search_jobs_handler(setup.update, setup.context)

        assert active_searches.get(setup.user.id, False) is False

    async def test_clears_active_search_on_error(
        self, handler_test_setup_factory, mock_orchestrator
    ):
        """Handler should clear active_searches even on error."""
        # mock_orchestrator defaults to has_cv=True; configure error
        mock_orchestrator.load_cv.side_effect = Exception("Load error")
        setup = handler_test_setup_factory(user_id=7303)

        await search_jobs_handler(setup.update, setup.context)

        assert active_searches.get(setup.user.id, False) is False


class TestSearchHandlerErrorHandling:
    """Tests for error handling in search handler."""

    async def test_handles_load_cv_error(self, handler_test_setup_factory, mock_orchestrator):
        """Handler should handle errors when loading CV."""
        # mock_orchestrator defaults to has_cv=True; configure error
        mock_orchestrator.load_cv.side_effect = Exception("Failed to load CV")
        setup = handler_test_setup_factory(user_id=7401)

        await search_jobs_handler(setup.update, setup.context)

        assert any("Error" in text or "error" in text for text in setup.message._reply_texts)

    async def test_handles_scrape_error(self, handler_test_setup_factory, mock_orchestrator):
        """Handler should handle errors during scraping."""
        # mock_orchestrator defaults to has_cv=True; configure scrape error
        mock_orchestrator.scrape_jobs_streaming.side_effect = Exception("Scrape failed")
        setup = handler_test_setup_factory(user_id=7402)

        await search_jobs_handler(setup.update, setup.context)

        assert any("Error" in text or "error" in text for text in setup.message._reply_texts)


class TestSearchHandlerWorkflow:
    """Tests for the search workflow."""

    async def test_sends_search_started_message(
        self, handler_test_setup_factory, mock_orchestrator
    ):
        """Handler should send search started message."""
        # mock_orchestrator defaults to has_cv=True
        setup = handler_test_setup_factory(user_id=7501)

        await search_jobs_handler(setup.update, setup.context)

        assert any("Starting job search" in text for text in setup.message._reply_texts)

    async def test_sends_cv_loaded_message(self, handler_test_setup_factory, mock_orchestrator):
        """Handler should send CV loaded message."""
        # mock_orchestrator defaults to has_cv=True
        setup = handler_test_setup_factory(user_id=7502)

        await search_jobs_handler(setup.update, setup.context)

        assert any("CV loaded" in text for text in setup.message._reply_texts)

    async def test_sends_completion_summary(self, handler_test_setup_factory, mock_orchestrator):
        """Handler should send completion summary."""
        # mock_orchestrator defaults to has_cv=True
        setup = handler_test_setup_factory(user_id=7503)

        await search_jobs_handler(setup.update, setup.context)

        assert any("completed" in text.lower() for text in setup.message._reply_texts)

    async def test_sends_no_relevant_jobs_message(
        self, handler_test_setup_factory, mock_orchestrator
    ):
        """Handler should send message when no relevant jobs found."""
        # mock_orchestrator defaults to has_cv=True, no jobs
        setup = handler_test_setup_factory(user_id=7504)

        await search_jobs_handler(setup.update, setup.context)

        assert any("No relevant jobs" in text for text in setup.message._reply_texts)


class TestSearchHandlerWithJobs:
    """Tests for search handler with actual job results."""

    async def test_processes_scraped_jobs(self, handler_test_setup_factory, mock_orchestrator):
        """Handler should process scraped jobs through the pipeline."""
        # mock_orchestrator defaults to has_cv=True; configure jobs
        jobs_batch = [{"id": 1, "title": "Developer"}]
        mock_orchestrator.scrape_jobs_streaming.return_value = iter([(jobs_batch, 1)])
        mock_orchestrator.filter_jobs_list.return_value = jobs_batch
        setup = handler_test_setup_factory(user_id=7601)

        await search_jobs_handler(setup.update, setup.context)

        mock_orchestrator.filter_jobs_list.assert_called()

    async def test_reports_scraped_job_count(self, handler_test_setup_factory, mock_orchestrator):
        """Handler should report the number of scraped jobs."""
        # mock_orchestrator defaults to has_cv=True; configure jobs
        jobs_batch = [{"id": i, "title": f"Job {i}"} for i in range(5)]
        mock_orchestrator.scrape_jobs_streaming.return_value = iter([(jobs_batch, 5)])
        setup = handler_test_setup_factory(user_id=7602)

        await search_jobs_handler(setup.update, setup.context)

        assert any("5" in text and "Scraped" in text for text in setup.message._reply_texts)

    async def test_reports_filtered_job_count(self, handler_test_setup_factory, mock_orchestrator):
        """Handler should report filtered job count."""
        # mock_orchestrator defaults to has_cv=True; configure jobs
        jobs_batch = [{"id": i} for i in range(10)]
        filtered_jobs = [{"id": i} for i in range(3)]
        mock_orchestrator.scrape_jobs_streaming.return_value = iter([(jobs_batch, 10)])
        mock_orchestrator.filter_jobs_list.return_value = filtered_jobs
        setup = handler_test_setup_factory(user_id=7603)

        await search_jobs_handler(setup.update, setup.context)

        assert any(
            "3" in text and "passed filters" in text.lower() for text in setup.message._reply_texts
        )

    async def test_sends_relevant_jobs(self, handler_test_setup_factory, mock_orchestrator):
        """Handler should send relevant jobs to user."""
        # mock_orchestrator defaults to has_cv=True; configure jobs with relevant result
        jobs_batch = [{"id": 1}]
        relevant_job = {
            "is_relevant": True,
            "job": {
                "title": "Python Developer",
                "company": {"name": "Test Corp"},
                "url": "https://example.com/job/1",
            },
        }
        mock_orchestrator.scrape_jobs_streaming.return_value = iter([(jobs_batch, 1)])
        mock_orchestrator.filter_jobs_list.return_value = jobs_batch
        mock_orchestrator.process_jobs_iterator.return_value = iter([(0, 1, relevant_job)])
        setup = handler_test_setup_factory(user_id=7604)

        await search_jobs_handler(setup.update, setup.context)

        assert any("Python Developer" in text for text in setup.message._reply_texts)
        assert any("Test Corp" in text for text in setup.message._reply_texts)


class TestSearchHandlerDaysParameter:
    """Tests for days parameter handling in search handler.

    The handler now passes `days` directly to the orchestrator, which handles
    date calculation internally. These tests verify the handler correctly passes
    the days parameter.

    REQ-2: Telegram bot passes days parameter as-is to orchestrator
    REQ-3: Handler passes None when days not specified
    """

    async def test_passes_none_days_when_not_provided(
        self, handler_test_setup_factory, mock_orchestrator
    ):
        """Handler should pass days=None when no days parameter is provided.

        The orchestrator will handle auto-calculation internally.
        """
        # mock_orchestrator defaults to has_cv=True
        setup = handler_test_setup_factory(user_id=8001, args=[])

        await search_jobs_handler(setup.update, setup.context)

        # Verify scrape_jobs_streaming was called with days=None
        call_args = mock_orchestrator.scrape_jobs_streaming.call_args
        days_arg = call_args[0][2]  # Third positional argument (days)
        assert days_arg is None, "days should be None when not provided"

    async def test_passes_explicit_days_to_orchestrator(
        self, handler_test_setup_factory, mock_orchestrator
    ):
        """Handler should pass explicit days value to orchestrator.

        REQ-2: When days=N is explicitly provided, pass it directly to orchestrator.
        """
        # mock_orchestrator defaults to has_cv=True
        setup = handler_test_setup_factory(user_id=8002, args=["days=7"])

        await search_jobs_handler(setup.update, setup.context)

        # Verify scrape_jobs_streaming was called with days=7
        call_args = mock_orchestrator.scrape_jobs_streaming.call_args
        days_arg = call_args[0][2]  # Third positional argument (days)
        assert days_arg == 7, "days should be 7 when explicitly provided"

    async def test_displays_default_date_range_message_when_days_none(
        self, handler_test_setup_factory, mock_orchestrator
    ):
        """Handler should display message for default date range when days=None.

        With simplified formatter, should show "Using default date range".
        """
        # mock_orchestrator defaults to has_cv=True
        setup = handler_test_setup_factory(user_id=8003, args=[])

        await search_jobs_handler(setup.update, setup.context)

        # Should contain message indicating default date range
        assert any(
            "default" in text.lower() or "using" in text.lower()
            for text in setup.message._reply_texts
        ), f"Expected default date range indicator in messages: {setup.message._reply_texts}"

    async def test_displays_explicit_days_in_message(
        self, handler_test_setup_factory, mock_orchestrator
    ):
        """Handler should display explicit days value in message."""
        # mock_orchestrator defaults to has_cv=True
        setup = handler_test_setup_factory(user_id=8004, args=["days=10"])

        await search_jobs_handler(setup.update, setup.context)

        # Should show "Last 10 days" or similar
        assert any(
            "10" in text and "days" in text.lower() for text in setup.message._reply_texts
        ), f"Expected '10 days' in messages: {setup.message._reply_texts}"
