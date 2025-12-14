"""Tests for search formatter functions."""

import pytest

from telegram_bot.handlers.search.formatter import (
    format_job_message,
    format_search_parameters,
    format_search_summary,
)


class TestFormatJobMessage:
    """Tests for format_job_message function."""

    @pytest.fixture
    def basic_job_result(self):
        """Create a basic job result fixture."""
        return {
            "is_relevant": True,
            "job": {
                "title": "Software Engineer",
                "company": {"name": "Tech Corp"},
                "url": "https://example.com/job/123",
            },
        }

    @pytest.fixture
    def full_job_result(self):
        """Create a complete job result with all fields."""
        return {
            "is_relevant": True,
            "job": {
                "title": "Senior Python Developer",
                "company": {"name": "Awesome Company"},
                "salary": {
                    "currency": "USD",
                    "min_value": 100000,
                    "max_value": 150000,
                },
                "location": {
                    "region": "San Francisco, CA",
                    "is_remote": True,
                },
                "employment_type": "Full-time",
                "url": "https://example.com/job/456",
            },
            "extracted_must_have_skills": ["Python", "Django", "PostgreSQL"],
            "extracted_nice_to_have_skills": ["React", "Docker"],
        }

    def test_includes_job_number(self, basic_job_result):
        """Message should include job number."""
        message = format_job_message(basic_job_result, 1, 5)
        assert "1/5" in message

    def test_includes_job_title(self, basic_job_result):
        """Message should include job title."""
        message = format_job_message(basic_job_result, 1, 1)
        assert "Software Engineer" in message

    def test_includes_company_name(self, basic_job_result):
        """Message should include company name."""
        message = format_job_message(basic_job_result, 1, 1)
        assert "Tech Corp" in message

    def test_includes_url(self, basic_job_result):
        """Message should include job URL."""
        message = format_job_message(basic_job_result, 1, 1)
        assert "https://example.com/job/123" in message

    def test_includes_salary_range(self, full_job_result):
        """Message should include salary range when available."""
        message = format_job_message(full_job_result, 1, 1)
        assert "USD" in message
        assert "100000" in message
        assert "150000" in message

    def test_includes_location(self, full_job_result):
        """Message should include location when available."""
        message = format_job_message(full_job_result, 1, 1)
        assert "San Francisco" in message

    def test_includes_remote_indicator(self, full_job_result):
        """Message should include remote indicator when applicable."""
        message = format_job_message(full_job_result, 1, 1)
        assert "Remote" in message

    def test_includes_employment_type(self, full_job_result):
        """Message should include employment type when available."""
        message = format_job_message(full_job_result, 1, 1)
        assert "Full-time" in message

    def test_includes_must_have_skills(self, full_job_result):
        """Message should include must-have skills."""
        message = format_job_message(full_job_result, 1, 1)
        assert "Python" in message
        assert "Django" in message
        assert "PostgreSQL" in message

    def test_includes_nice_to_have_skills(self, full_job_result):
        """Message should include nice-to-have skills."""
        message = format_job_message(full_job_result, 1, 1)
        assert "React" in message
        assert "Docker" in message

    def test_truncates_long_skill_lists(self):
        """Message should truncate skill lists longer than 10 items."""
        job_result = {
            "is_relevant": True,
            "job": {
                "title": "Developer",
                "company": {"name": "Corp"},
                "url": "https://example.com",
            },
            "extracted_must_have_skills": [f"Skill{i}" for i in range(15)],
            "extracted_nice_to_have_skills": [],
        }
        message = format_job_message(job_result, 1, 1)
        assert "5 more" in message

    def test_handles_missing_company_name(self):
        """Message should handle missing company name gracefully."""
        job_result = {
            "is_relevant": True,
            "job": {
                "title": "Developer",
                "company": {},
                "url": "https://example.com",
            },
        }
        message = format_job_message(job_result, 1, 1)
        assert "N/A" in message

    def test_handles_missing_salary(self, basic_job_result):
        """Message should handle missing salary gracefully."""
        message = format_job_message(basic_job_result, 1, 1)
        assert "Salary" not in message or "N/A" in message

    def test_handles_salary_without_max(self):
        """Message should handle salary without max value."""
        job_result = {
            "is_relevant": True,
            "job": {
                "title": "Developer",
                "company": {"name": "Corp"},
                "salary": {"currency": "EUR", "min_value": 50000},
                "url": "https://example.com",
            },
        }
        message = format_job_message(job_result, 1, 1)
        assert "EUR" in message
        assert "50000" in message


class TestFormatSearchSummary:
    """Tests for format_search_summary function."""

    def test_includes_total_scraped(self):
        """Summary should include total scraped count."""
        summary = format_search_summary(100, 50, 25, 10)
        assert "100" in summary

    def test_includes_passed_filters(self):
        """Summary should include passed filters count."""
        summary = format_search_summary(100, 50, 25, 10)
        assert "50" in summary

    def test_includes_processed_count(self):
        """Summary should include processed count."""
        summary = format_search_summary(100, 50, 25, 10)
        assert "25" in summary

    def test_includes_relevant_count(self):
        """Summary should include relevant jobs count."""
        summary = format_search_summary(100, 50, 25, 10)
        assert "10" in summary

    def test_indicates_completion(self):
        """Summary should indicate search completion."""
        summary = format_search_summary(0, 0, 0, 0)
        assert "completed" in summary.lower()

    def test_handles_zero_values(self):
        """Summary should handle zero values gracefully."""
        summary = format_search_summary(0, 0, 0, 0)
        assert "0" in summary


class TestFormatSearchParameters:
    """Tests for format_search_parameters function."""

    def test_includes_min_salary(self):
        """Parameters message should include minimum salary."""
        message = format_search_parameters(5000, "remote", 7)
        assert "5000" in message

    def test_includes_employment_location(self):
        """Parameters message should include employment location."""
        message = format_search_parameters(5000, "remote", 7)
        assert "remote" in message.lower()

    def test_includes_days_when_specified(self):
        """Parameters message should include days when specified."""
        message = format_search_parameters(5000, "remote", 7)
        assert "7" in message

    def test_handles_none_days(self):
        """Parameters message should handle None days."""
        message = format_search_parameters(5000, "remote", None)
        assert "all" in message.lower() or "All" in message

    def test_indicates_search_starting(self):
        """Parameters message should indicate search is starting."""
        message = format_search_parameters(5000, "remote", 1)
        assert "Starting" in message or "search" in message.lower()

    def test_includes_time_warning(self):
        """Parameters message should include time warning."""
        message = format_search_parameters(5000, "remote", 1)
        assert "minute" in message.lower() or "take" in message.lower()
