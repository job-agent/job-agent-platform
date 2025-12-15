"""Tests for job filter service."""

import pytest

from .filter import FilterService
from .filter_config import FilterConfig


class TestFilterService:
    """Test suite for job filtering functionality."""

    def _apply_filter(self, jobs, config):
        service = FilterService()
        service.configure(config)
        return service.filter(jobs)

    def test_filter_with_no_config_returns_all_jobs(self, sample_jobs_list):
        """Test that filtering with no config returns all jobs."""
        result = self._apply_filter(sample_jobs_list, None)
        assert len(result) == len(sample_jobs_list)
        assert result == sample_jobs_list

    def test_filter_with_empty_config_returns_all_jobs(self, sample_jobs_list):
        """Test that filtering with empty config returns all jobs."""
        result = self._apply_filter(sample_jobs_list, {})
        assert len(result) == len(sample_jobs_list)
        assert result == sample_jobs_list

    def test_filter_by_max_experience_months(self, sample_jobs_list):
        """Test filtering by maximum experience months."""
        config: FilterConfig = {"max_months_of_experience": 36}
        result = self._apply_filter(sample_jobs_list, config)

        assert len(result) == 2
        assert all(job["experience_months"] <= 36 for job in result)
        assert result[0]["job_id"] == 1
        assert result[1]["job_id"] == 2

    def test_filter_by_max_experience_excludes_higher(self, sample_jobs_list):
        """Test that max experience filter excludes jobs with higher requirements."""
        config: FilterConfig = {"max_months_of_experience": 24}
        result = self._apply_filter(sample_jobs_list, config)

        assert len(result) == 1
        assert result[0]["job_id"] == 1
        assert result[0]["experience_months"] == 12

    def test_filter_by_location_allows_to_apply(self, sample_jobs_list):
        """Test filtering by location allows to apply."""
        config: FilterConfig = {"location_allows_to_apply": True}
        result = self._apply_filter(sample_jobs_list, config)

        assert len(result) == 3
        assert all(job["location"]["can_apply"] is True for job in result)
        assert 3 not in [job["job_id"] for job in result]

    def test_filter_by_multiple_criteria(self, sample_jobs_list):
        """Test filtering by multiple criteria simultaneously."""
        config: FilterConfig = {
            "max_months_of_experience": 36,
            "location_allows_to_apply": True,
        }
        result = self._apply_filter(sample_jobs_list, config)

        assert len(result) == 2
        assert all(job["experience_months"] <= 36 for job in result)
        assert all(job["location"]["can_apply"] is True for job in result)
        assert result[0]["job_id"] == 1
        assert result[1]["job_id"] == 2

    def test_filter_very_strict_criteria_returns_few_jobs(self, sample_jobs_list):
        """Test that very strict criteria filters out most jobs."""
        config: FilterConfig = {
            "max_months_of_experience": 15,
            "location_allows_to_apply": True,
        }
        result = self._apply_filter(sample_jobs_list, config)

        assert len(result) == 1
        assert result[0]["job_id"] == 1

    def test_filter_impossible_criteria_returns_empty_list(self, sample_jobs_list):
        """Test that impossible criteria returns empty list."""
        config: FilterConfig = {
            "max_months_of_experience": 0,
        }
        result = self._apply_filter(sample_jobs_list, config)

        assert len(result) == 0
        assert result == []

    def test_filter_with_missing_location_data(self):
        """Test filtering when some jobs have missing location data."""
        jobs = [
            {"job_id": 1, "experience_months": 12, "location": {"can_apply": True}},
            {"job_id": 2, "experience_months": 24, "location": {}},
            {"job_id": 3, "experience_months": 36},
        ]

        config: FilterConfig = {"location_allows_to_apply": True}
        result = self._apply_filter(jobs, config)

        assert len(result) == 1
        assert result[0]["job_id"] == 1

    def test_filter_with_missing_experience_data(self):
        """Test filtering when some jobs have missing experience data."""
        jobs = [
            {"job_id": 1, "experience_months": 12, "location": {"can_apply": True}},
            {"job_id": 2, "location": {"can_apply": True}},
        ]

        config: FilterConfig = {"max_months_of_experience": 24}
        result = self._apply_filter(jobs, config)

        assert len(result) == 2

    def test_filter_location_allows_false_keeps_jobs_when_not_required(self, sample_jobs_list):
        """Test that location_allows_to_apply=False doesn't filter anything."""
        config: FilterConfig = {"location_allows_to_apply": False}
        result = self._apply_filter(sample_jobs_list, config)

        assert len(result) == len(sample_jobs_list)

    def test_filter_preserves_job_data_structure(self, sample_jobs_list):
        """Test that filtering preserves complete job data structure."""
        config: FilterConfig = {"max_months_of_experience": 36}
        result = self._apply_filter(sample_jobs_list, config)

        for job in result:
            assert "job_id" in job
            assert "title" in job
            assert "experience_months" in job
            assert "location" in job
            assert isinstance(job["location"], dict)

    def test_filter_with_edge_case_experience_values(self):
        """Test filtering with edge case experience values."""
        jobs = [
            {"job_id": 1, "experience_months": 0},
            {"job_id": 2, "experience_months": 24},
            {"job_id": 3, "experience_months": 25},
        ]

        config: FilterConfig = {"max_months_of_experience": 24}
        result = self._apply_filter(jobs, config)

        assert len(result) == 2
        assert result[0]["job_id"] == 1
        assert result[1]["job_id"] == 2

    def test_filter_with_realistic_job_data(self, sample_job_dict):
        """Test filtering with realistic job dictionary structure."""
        jobs = [sample_job_dict]
        config: FilterConfig = {
            "max_months_of_experience": 48,
            "location_allows_to_apply": True,
        }
        result = self._apply_filter(jobs, config)

        assert len(result) == 1
        assert result[0]["job_id"] == sample_job_dict["job_id"]
        assert result[0]["title"] == sample_job_dict["title"]

    def test_filter_excludes_jobs_present_in_repository(self):
        class StubRepository:
            def __init__(self):
                self.external_ids = {"100"}
                self.active_pairs = {("Duplicate Title", "Company A")}

            def get_by_external_id(self, external_id, source=None):
                if external_id in self.external_ids:
                    return {"external_id": external_id}
                return None

            def has_active_job_with_title_and_company(self, title, company_name):
                return (title, company_name) in self.active_pairs

        service = FilterService(job_repository_factory=lambda: StubRepository())

        jobs = [
            {
                "job_id": 50,
                "title": "First Job",
                "experience_months": 12,
                "location": {"can_apply": True},
                "company": {"name": "Company X"},
            },
            {
                "job_id": 100,
                "title": "Duplicate External",
                "experience_months": 12,
                "location": {"can_apply": True},
                "company": {"name": "Company Y"},
            },
            {
                "job_id": 200,
                "title": "Duplicate Title",
                "experience_months": 12,
                "location": {"can_apply": True},
                "company": {"name": "Company A"},
            },
        ]

        result = service.filter(jobs)

        assert len(result) == 1
        assert result[0]["job_id"] == 50

    def test_constructor_applies_default_config(self):
        """Test that constructor sets default filter configuration."""
        service = FilterService()

        assert service.config["max_months_of_experience"] == 60
        assert service.config["location_allows_to_apply"] is True

    def test_filter_raises_when_repository_factory_throws(self):
        """Test that exception from repository factory propagates."""

        def failing_factory():
            raise RuntimeError("Factory failure")

        service = FilterService(job_repository_factory=failing_factory)
        jobs = [{"job_id": 1, "experience_months": 12, "location": {"can_apply": True}}]

        with pytest.raises(RuntimeError, match="Factory failure"):
            service.filter(jobs)

    def test_filter_raises_when_get_by_external_id_throws(self):
        """Test that exception from repository.get_by_external_id propagates."""

        class FailingRepository:
            def get_by_external_id(self, external_id, source=None):
                raise RuntimeError("get_by_external_id failure")

        service = FilterService(job_repository_factory=lambda: FailingRepository())
        jobs = [{"job_id": 1, "experience_months": 12, "location": {"can_apply": True}}]

        with pytest.raises(RuntimeError, match="get_by_external_id failure"):
            service.filter(jobs)

    def test_filter_raises_when_has_active_job_throws(self):
        """Test that exception from repository.has_active_job_with_title_and_company propagates."""

        class FailingRepository:
            def get_by_external_id(self, external_id, source=None):
                return None

            def has_active_job_with_title_and_company(self, title, company_name):
                raise RuntimeError("has_active_job failure")

        service = FilterService(job_repository_factory=lambda: FailingRepository())
        jobs = [
            {
                "job_id": 1,
                "title": "Test Job",
                "experience_months": 12,
                "location": {"can_apply": True},
                "company": {"name": "Test Company"},
            }
        ]

        with pytest.raises(RuntimeError, match="has_active_job failure"):
            service.filter(jobs)

    def test_filter_raises_when_experience_months_is_none(self):
        """Test that explicit None for experience_months raises TypeError."""
        service = FilterService()
        service.configure({"max_months_of_experience": 60})
        jobs = [{"job_id": 1, "experience_months": None, "location": {"can_apply": True}}]

        with pytest.raises(TypeError):
            service.filter(jobs)

    def test_filter_raises_when_location_is_none(self):
        """Test that explicit None for location raises AttributeError."""
        service = FilterService()
        service.configure({"location_allows_to_apply": True})
        jobs = [{"job_id": 1, "experience_months": 12, "location": None}]

        with pytest.raises(AttributeError):
            service.filter(jobs)

    def test_filter_excludes_previously_stored_irrelevant_jobs(self):
        """Test that previously stored irrelevant jobs are filtered out.

        When a job was previously processed and stored as irrelevant (is_relevant=False),
        it should still be excluded from future searches to avoid re-processing.
        """

        class StubRepository:
            def __init__(self):
                # Simulates a job that was stored as irrelevant
                self.stored_jobs = {
                    "123": {"external_id": "123", "is_relevant": False},
                }

            def get_by_external_id(self, external_id, source=None):
                # Returns the job regardless of is_relevant value
                return self.stored_jobs.get(external_id)

            def has_active_job_with_title_and_company(self, title, company_name):
                return False

        service = FilterService(job_repository_factory=lambda: StubRepository())

        jobs = [
            {
                "job_id": 123,  # Same as stored irrelevant job
                "title": "Previously Irrelevant Job",
                "experience_months": 12,
                "location": {"can_apply": True},
                "company": {"name": "Some Company"},
            },
            {
                "job_id": 456,  # New job
                "title": "New Job",
                "experience_months": 12,
                "location": {"can_apply": True},
                "company": {"name": "Another Company"},
            },
        ]

        result = service.filter(jobs)

        # Only the new job should pass through; the stored irrelevant job is excluded
        assert len(result) == 1
        assert result[0]["job_id"] == 456


class TestFilterServiceWithRejected:
    """Tests for filter_with_rejected method.

    These tests verify the NEW behavior where the filter service returns
    both passed and rejected (filtered) jobs, allowing the caller to
    store rejected jobs for future exclusion.
    """

    def test_filter_with_rejected_returns_tuple_of_two_lists(self, sample_jobs_list):
        """Test that filter_with_rejected returns a tuple of (passed, rejected) lists."""
        service = FilterService()
        service.configure({"max_months_of_experience": 36})

        result = service.filter_with_rejected(sample_jobs_list)

        assert isinstance(result, tuple)
        assert len(result) == 2
        passed, rejected = result
        assert isinstance(passed, list)
        assert isinstance(rejected, list)

    def test_filter_with_rejected_passed_jobs_match_filter_output(self, sample_jobs_list):
        """Test that passed jobs from filter_with_rejected match regular filter output."""
        service = FilterService()
        config = {"max_months_of_experience": 36}
        service.configure(config)

        passed, _ = service.filter_with_rejected(sample_jobs_list)
        regular_filtered = service.filter(sample_jobs_list)

        assert passed == regular_filtered

    def test_filter_with_rejected_experience_check_populates_rejected(self, sample_jobs_list):
        """Test that jobs failing experience check appear in rejected list."""
        service = FilterService()
        service.configure({"max_months_of_experience": 36})

        passed, rejected = service.filter_with_rejected(sample_jobs_list)

        # Jobs with experience > 36 should be in rejected
        rejected_ids = [job["job_id"] for job in rejected]
        assert 3 in rejected_ids  # 60 months
        assert 4 in rejected_ids  # 96 months

        # Jobs with experience <= 36 should NOT be in rejected
        assert 1 not in rejected_ids  # 12 months
        assert 2 not in rejected_ids  # 36 months

    def test_filter_with_rejected_location_check_populates_rejected(self, sample_jobs_list):
        """Test that jobs failing location check appear in rejected list."""
        service = FilterService()
        service.configure({"location_allows_to_apply": True})

        passed, rejected = service.filter_with_rejected(sample_jobs_list)

        # Job with can_apply=False should be in rejected
        rejected_ids = [job["job_id"] for job in rejected]
        assert 3 in rejected_ids  # can_apply=False

        # Jobs with can_apply=True should NOT be in rejected for location
        # (though they might be rejected for other reasons)
        passed_ids = [job["job_id"] for job in passed]
        assert 1 in passed_ids
        assert 2 in passed_ids
        assert 4 in passed_ids

    def test_filter_with_rejected_both_criteria_populates_rejected(self, sample_jobs_list):
        """Test that jobs failing multiple criteria appear in rejected list."""
        service = FilterService()
        service.configure(
            {
                "max_months_of_experience": 36,
                "location_allows_to_apply": True,
            }
        )

        passed, rejected = service.filter_with_rejected(sample_jobs_list)

        # Passed: jobs 1 and 2 (experience <= 36 AND can_apply=True)
        passed_ids = [job["job_id"] for job in passed]
        assert 1 in passed_ids
        assert 2 in passed_ids
        assert len(passed) == 2

        # Rejected: jobs 3 and 4
        rejected_ids = [job["job_id"] for job in rejected]
        assert 3 in rejected_ids  # can_apply=False (and experience=60)
        assert 4 in rejected_ids  # experience=96

    def test_filter_with_rejected_preserves_job_data_structure(self, sample_jobs_list):
        """Test that rejected jobs preserve complete job data structure."""
        service = FilterService()
        service.configure({"max_months_of_experience": 24})

        _, rejected = service.filter_with_rejected(sample_jobs_list)

        for job in rejected:
            assert "job_id" in job
            assert "title" in job
            assert "experience_months" in job
            assert "location" in job

    def test_filter_with_rejected_sum_equals_input(self, sample_jobs_list):
        """Test that passed + rejected equals original input count."""
        service = FilterService()
        service.configure({"max_months_of_experience": 36})

        passed, rejected = service.filter_with_rejected(sample_jobs_list)

        assert len(passed) + len(rejected) == len(sample_jobs_list)

    def test_filter_with_rejected_empty_input_returns_empty_lists(self):
        """Test that empty input returns two empty lists."""
        service = FilterService()
        service.configure({"max_months_of_experience": 36})

        passed, rejected = service.filter_with_rejected([])

        assert passed == []
        assert rejected == []

    def test_filter_with_rejected_no_rejections(self):
        """Test filter_with_rejected when all jobs pass."""
        jobs = [
            {"job_id": 1, "experience_months": 12, "location": {"can_apply": True}},
            {"job_id": 2, "experience_months": 24, "location": {"can_apply": True}},
        ]
        service = FilterService()
        service.configure({"max_months_of_experience": 36})

        passed, rejected = service.filter_with_rejected(jobs)

        assert len(passed) == 2
        assert len(rejected) == 0

    def test_filter_with_rejected_all_rejected(self):
        """Test filter_with_rejected when all jobs are rejected."""
        jobs = [
            {"job_id": 1, "experience_months": 120, "location": {"can_apply": True}},
            {"job_id": 2, "experience_months": 96, "location": {"can_apply": True}},
        ]
        service = FilterService()
        service.configure({"max_months_of_experience": 36})

        passed, rejected = service.filter_with_rejected(jobs)

        assert len(passed) == 0
        assert len(rejected) == 2

    def test_filter_with_rejected_excludes_existing_jobs_into_neither_list(self):
        """Test that existing repository jobs are excluded from BOTH lists.

        Jobs that already exist in the repository should not appear in either
        passed or rejected lists - they're simply skipped.
        """

        class StubRepository:
            def __init__(self):
                self.external_ids = {"100"}

            def get_by_external_id(self, external_id, source=None):
                if external_id in self.external_ids:
                    return {"external_id": external_id}
                return None

            def has_active_job_with_title_and_company(self, title, company_name):
                return False

        service = FilterService(job_repository_factory=lambda: StubRepository())
        service.configure({"max_months_of_experience": 60})

        jobs = [
            {
                "job_id": 100,  # Exists in repository
                "title": "Existing Job",
                "experience_months": 12,
                "location": {"can_apply": True},
                "company": {"name": "Company X"},
            },
            {
                "job_id": 200,  # New job, passes filter
                "title": "New Passing Job",
                "experience_months": 24,
                "location": {"can_apply": True},
                "company": {"name": "Company Y"},
            },
            {
                "job_id": 300,  # New job, fails filter
                "title": "New Failing Job",
                "experience_months": 120,
                "location": {"can_apply": True},
                "company": {"name": "Company Z"},
            },
        ]

        passed, rejected = service.filter_with_rejected(jobs)

        # Existing job (100) should be in neither list
        all_ids = [job["job_id"] for job in passed + rejected]
        assert 100 not in all_ids

        # New passing job should be in passed
        passed_ids = [job["job_id"] for job in passed]
        assert 200 in passed_ids

        # New failing job should be in rejected
        rejected_ids = [job["job_id"] for job in rejected]
        assert 300 in rejected_ids
