"""Integration tests for job filter service."""

from job_agent_backend.filter_service.filter import FilterService
from job_agent_backend.filter_service.filter_config import FilterConfig


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

        # Should include jobs with 12 and 36 months experience
        assert len(result) == 2
        assert all(job["experience_months"] <= 36 for job in result)
        assert result[0]["job_id"] == 1
        assert result[1]["job_id"] == 2

    def test_filter_by_max_experience_excludes_higher(self, sample_jobs_list):
        """Test that max experience filter excludes jobs with higher requirements."""
        config: FilterConfig = {"max_months_of_experience": 24}
        result = self._apply_filter(sample_jobs_list, config)

        # Should only include job with 12 months experience
        assert len(result) == 1
        assert result[0]["job_id"] == 1
        assert result[0]["experience_months"] == 12

    def test_filter_by_location_allows_to_apply(self, sample_jobs_list):
        """Test filtering by location allows to apply."""
        config: FilterConfig = {"location_allows_to_apply": True}
        result = self._apply_filter(sample_jobs_list, config)

        # Should exclude job_id 3 (can_apply=False)
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

        # Should only include jobs 1 and 2 (both meet both criteria)
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

        # Should only include job 1
        assert len(result) == 1
        assert result[0]["job_id"] == 1

    def test_filter_impossible_criteria_returns_empty_list(self, sample_jobs_list):
        """Test that impossible criteria returns empty list."""
        config: FilterConfig = {
            "max_months_of_experience": 0,  # No job has 0 experience requirement
        }
        result = self._apply_filter(sample_jobs_list, config)

        assert len(result) == 0
        assert result == []

    def test_filter_with_missing_location_data(self):
        """Test filtering when some jobs have missing location data."""
        jobs = [
            {"job_id": 1, "experience_months": 12, "location": {"can_apply": True}},
            {"job_id": 2, "experience_months": 24, "location": {}},  # Missing can_apply
            {"job_id": 3, "experience_months": 36},  # Missing location entirely
        ]

        config: FilterConfig = {"location_allows_to_apply": True}
        result = self._apply_filter(jobs, config)

        # Should only include job 1
        assert len(result) == 1
        assert result[0]["job_id"] == 1

    def test_filter_with_missing_experience_data(self):
        """Test filtering when some jobs have missing experience data."""
        jobs = [
            {"job_id": 1, "experience_months": 12, "location": {"can_apply": True}},
            {"job_id": 2, "location": {"can_apply": True}},  # Missing experience_months
        ]

        config: FilterConfig = {"max_months_of_experience": 24}
        result = self._apply_filter(jobs, config)

        # Should include both (missing experience defaults to 0)
        assert len(result) == 2

    def test_filter_location_allows_false_keeps_jobs_when_not_required(self, sample_jobs_list):
        """Test that location_allows_to_apply=False doesn't filter anything."""
        config: FilterConfig = {"location_allows_to_apply": False}
        result = self._apply_filter(sample_jobs_list, config)

        # Should return all jobs (filter only active when True)
        assert len(result) == len(sample_jobs_list)

    def test_filter_preserves_job_data_structure(self, sample_jobs_list):
        """Test that filtering preserves complete job data structure."""
        config: FilterConfig = {"max_months_of_experience": 36}
        result = self._apply_filter(sample_jobs_list, config)

        # Verify all fields are preserved
        for job in result:
            assert "job_id" in job
            assert "title" in job
            assert "experience_months" in job
            assert "location" in job
            assert isinstance(job["location"], dict)

    def test_filter_with_edge_case_experience_values(self):
        """Test filtering with edge case experience values."""
        jobs = [
            {"job_id": 1, "experience_months": 0},  # Exactly 0
            {"job_id": 2, "experience_months": 24},  # Exactly at limit
            {"job_id": 3, "experience_months": 25},  # Just over limit
        ]

        config: FilterConfig = {"max_months_of_experience": 24}
        result = self._apply_filter(jobs, config)

        # Should include jobs 1 and 2
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
