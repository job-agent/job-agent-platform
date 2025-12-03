"""Tests for JobMapper class."""

from datetime import datetime, UTC

import pytest

from jobs_repository.mapper import JobMapper


class TestJobMapper:
    """Test suite for JobMapper class."""

    @pytest.fixture
    def mapper(self):
        """Create a JobMapper instance."""
        return JobMapper()

    @pytest.fixture
    def complete_job_dict(self):
        """Sample complete JobDict data."""
        return {
            "job_id": 12345,
            "title": "Senior Software Engineer",
            "description": "We are looking for an experienced engineer.",
            "url": "https://example.com/jobs/12345",
            "source": "LinkedIn",
            "employment_type": "FULL_TIME",
            "experience_months": 36,
            "company": {"name": "Tech Corp", "website": "https://techcorp.com"},
            "location": {"region": "San Francisco, CA", "is_remote": True},
            "category": "Software Development",
            "industry": "Technology",
            "salary": {"currency": "USD", "min_value": 120000.0, "max_value": 160000.0},
            "date_posted": "2024-01-15T10:00:00Z",
            "valid_through": "2024-02-15T10:00:00Z",
            "must_have_skills": ["Python", "Django", "PostgreSQL"],
            "nice_to_have_skills": ["Docker", "AWS"],
        }

    @pytest.fixture
    def minimal_job_dict(self):
        """Sample minimal JobDict data."""
        return {
            "job_id": 999,
            "title": "Job Title",
        }

    def test_map_to_model_with_complete_data(self, mapper, complete_job_dict):
        """Test mapping complete JobDict to model format."""
        result = mapper.map_to_model(complete_job_dict)

        assert result["title"] == "Senior Software Engineer"
        assert result["description"] == "We are looking for an experienced engineer."
        assert result["external_id"] == "12345"
        assert result["source_url"] == "https://example.com/jobs/12345"
        assert result["source"] == "LinkedIn"
        assert result["job_type"] == "FULL_TIME"
        assert result["experience_months"] == 36
        assert result["company_name"] == "Tech Corp"
        assert result["location_region"] == "San Francisco, CA"
        assert result["is_remote"] is True
        assert result["category_name"] == "Software Development"
        assert result["industry_name"] == "Technology"
        assert result["salary_currency"] == "USD"
        assert result["salary_min"] == 120000.0
        assert result["salary_max"] == 160000.0
        assert result["must_have_skills"] == ["Python", "Django", "PostgreSQL"]
        assert result["nice_to_have_skills"] == ["Docker", "AWS"]
        assert isinstance(result["posted_at"], datetime)
        assert isinstance(result["expires_at"], datetime)

    def test_map_to_model_with_minimal_data(self, mapper, minimal_job_dict):
        """Test mapping minimal JobDict to model format."""
        result = mapper.map_to_model(minimal_job_dict)

        assert result["title"] == "Job Title"
        assert result["external_id"] == "999"
        assert result["description"] is None
        assert result["source_url"] is None
        assert "company_name" not in result
        assert "location_region" not in result
        assert "category_name" not in result
        assert "industry_name" not in result

    def test_map_simple_fields(self, mapper):
        """Test mapping of simple scalar fields."""
        job_data = {
            "job_id": 123,
            "title": "Test Job",
            "description": "Test Description",
            "url": "https://test.com",
            "source": "TestSource",
            "employment_type": "CONTRACT",
            "experience_months": 24,
        }

        result = mapper.map_to_model(job_data)

        assert result["title"] == "Test Job"
        assert result["description"] == "Test Description"
        assert result["external_id"] == "123"
        assert result["source_url"] == "https://test.com"
        assert result["source"] == "TestSource"
        assert result["job_type"] == "CONTRACT"
        assert result["experience_months"] == 24

    def test_external_id_converts_to_string(self, mapper):
        """Test that job_id is converted to string for external_id."""
        job_data = {"job_id": 12345, "title": "Test"}

        result = mapper.map_to_model(job_data)

        assert result["external_id"] == "12345"
        assert isinstance(result["external_id"], str)

    def test_map_company(self, mapper):
        """Test mapping of company data."""
        job_data = {
            "job_id": 1,
            "title": "Test",
            "company": {"name": "Example Corp", "website": "https://example.com"},
        }

        result = mapper.map_to_model(job_data)

        assert result["company_name"] == "Example Corp"

    def test_map_company_with_missing_company(self, mapper):
        """Test mapping when company data is missing."""
        job_data = {"job_id": 1, "title": "Test"}

        result = mapper.map_to_model(job_data)

        assert "company_name" not in result

    def test_map_location_with_region(self, mapper):
        """Test mapping of location with region."""
        job_data = {
            "job_id": 1,
            "title": "Test",
            "location": {"region": "New York, NY", "is_remote": False},
        }

        result = mapper.map_to_model(job_data)

        assert result["location_region"] == "New York, NY"
        assert result["is_remote"] is False

    def test_map_location_with_remote_only(self, mapper):
        """Test mapping of location with only is_remote."""
        job_data = {"job_id": 1, "title": "Test", "location": {"is_remote": True}}

        result = mapper.map_to_model(job_data)

        assert "location_region" not in result
        assert result["is_remote"] is True

    def test_map_location_defaults_is_remote_to_false(self, mapper):
        """Test that is_remote defaults to False when not provided."""
        job_data = {"job_id": 1, "title": "Test", "location": {"region": "Seattle, WA"}}

        result = mapper.map_to_model(job_data)

        assert result["is_remote"] is False

    def test_map_location_with_missing_location(self, mapper):
        """Test mapping when location data is missing."""
        job_data = {"job_id": 1, "title": "Test"}

        result = mapper.map_to_model(job_data)

        assert "location_region" not in result
        assert "is_remote" not in result

    def test_map_category(self, mapper):
        """Test mapping of category."""
        job_data = {"job_id": 1, "title": "Test", "category": "Engineering"}

        result = mapper.map_to_model(job_data)

        assert result["category_name"] == "Engineering"

    def test_map_category_with_missing_category(self, mapper):
        """Test mapping when category is missing."""
        job_data = {"job_id": 1, "title": "Test"}

        result = mapper.map_to_model(job_data)

        assert "category_name" not in result

    def test_map_industry(self, mapper):
        """Test mapping of industry."""
        job_data = {"job_id": 1, "title": "Test", "industry": "Finance"}

        result = mapper.map_to_model(job_data)

        assert result["industry_name"] == "Finance"

    def test_map_industry_with_missing_industry(self, mapper):
        """Test mapping when industry is missing."""
        job_data = {"job_id": 1, "title": "Test"}

        result = mapper.map_to_model(job_data)

        assert "industry_name" not in result

    def test_map_salary(self, mapper):
        """Test mapping of salary data."""
        job_data = {
            "job_id": 1,
            "title": "Test",
            "salary": {"currency": "EUR", "min_value": 50000.0, "max_value": 70000.0},
        }

        result = mapper.map_to_model(job_data)

        assert result["salary_currency"] == "EUR"
        assert result["salary_min"] == 50000.0
        assert result["salary_max"] == 70000.0

    def test_map_salary_defaults_currency_to_usd(self, mapper):
        """Test that salary currency defaults to USD."""
        job_data = {"job_id": 1, "title": "Test", "salary": {"min_value": 60000.0}}

        result = mapper.map_to_model(job_data)

        assert result["salary_currency"] == "USD"

    def test_map_salary_with_missing_salary(self, mapper):
        """Test mapping when salary data is missing."""
        job_data = {"job_id": 1, "title": "Test"}

        result = mapper.map_to_model(job_data)

        assert "salary_currency" not in result
        assert "salary_min" not in result
        assert "salary_max" not in result

    def test_map_datetime_fields(self, mapper):
        """Test mapping of datetime fields."""
        job_data = {
            "job_id": 1,
            "title": "Test",
            "date_posted": "2024-01-15T10:30:00Z",
            "valid_through": "2024-02-15T10:30:00Z",
        }

        result = mapper.map_to_model(job_data)

        assert isinstance(result["posted_at"], datetime)
        assert isinstance(result["expires_at"], datetime)
        assert result["posted_at"].year == 2024
        assert result["posted_at"].month == 1
        assert result["posted_at"].day == 15
        assert result["expires_at"].year == 2024
        assert result["expires_at"].month == 2
        assert result["expires_at"].day == 15

    def test_map_datetime_with_missing_dates(self, mapper):
        """Test mapping when datetime fields are missing."""
        job_data = {"job_id": 1, "title": "Test"}

        result = mapper.map_to_model(job_data)

        assert "posted_at" not in result
        assert "expires_at" not in result

    def test_map_must_have_skills(self, mapper):
        """Test mapping of must_have_skills."""
        job_data = {
            "job_id": 1,
            "title": "Test",
            "must_have_skills": ["Python", "SQL", "Git"],
        }

        result = mapper.map_to_model(job_data)

        assert result["must_have_skills"] == ["Python", "SQL", "Git"]

    def test_map_nice_to_have_skills(self, mapper):
        """Test mapping of nice_to_have_skills."""
        job_data = {
            "job_id": 1,
            "title": "Test",
            "nice_to_have_skills": ["React", "TypeScript"],
        }

        result = mapper.map_to_model(job_data)

        assert result["nice_to_have_skills"] == ["React", "TypeScript"]

    def test_empty_skills_arrays_not_mapped(self, mapper):
        """Test that empty skills arrays are not included in mapping."""
        job_data = {
            "job_id": 1,
            "title": "Test",
            "must_have_skills": [],
            "nice_to_have_skills": [],
        }

        result = mapper.map_to_model(job_data)

        assert "must_have_skills" not in result
        assert "nice_to_have_skills" not in result

    def test_none_values_are_preserved(self, mapper):
        """Test that None values are preserved in mapping."""
        job_data = {
            "job_id": 1,
            "title": "Test",
            "description": None,
            "url": None,
            "source": None,
            "employment_type": None,
            "experience_months": None,
        }

        result = mapper.map_to_model(job_data)

        assert result["description"] is None
        assert result["source_url"] is None
        assert result["source"] is None
        assert result["job_type"] is None
        assert result["experience_months"] is None

    def test_map_with_dict_input(self, mapper, complete_job_dict):
        """Test that mapper accepts plain dict."""
        result = mapper.map_to_model(complete_job_dict)

        assert result["title"] == "Senior Software Engineer"
        assert result["external_id"] == "12345"

    def test_datetime_parsing_with_timezone(self, mapper):
        """Test datetime parsing with different timezone formats."""
        job_data = {
            "job_id": 1,
            "title": "Test",
            "date_posted": "2024-01-15T10:30:00+00:00",
        }

        result = mapper.map_to_model(job_data)

        assert isinstance(result["posted_at"], datetime)
        assert result["posted_at"].year == 2024

    def test_all_mapping_methods_called(self, mapper, complete_job_dict):
        """Test that all private mapping methods are invoked."""
        result = mapper.map_to_model(complete_job_dict)

        assert "title" in result
        assert "company_name" in result
        assert "location_region" in result
        assert "category_name" in result
        assert "industry_name" in result
        assert "salary_currency" in result
        assert "posted_at" in result

    def test_missing_optional_fields_handled_gracefully(self, mapper):
        """Test that missing optional fields don't cause errors."""
        job_data = {"job_id": 1, "title": "Minimal Job"}

        result = mapper.map_to_model(job_data)

        assert result["title"] == "Minimal Job"
        assert result["external_id"] == "1"

    def test_integer_job_id_converted_to_string(self, mapper):
        """Test that integer job_id is converted to string."""
        job_data = {"job_id": 999999, "title": "Test"}

        result = mapper.map_to_model(job_data)

        assert result["external_id"] == "999999"
        assert isinstance(result["external_id"], str)

    def test_salary_with_partial_data(self, mapper):
        """Test salary mapping with only some fields."""
        job_data = {"job_id": 1, "title": "Test", "salary": {"min_value": 50000.0}}

        result = mapper.map_to_model(job_data)

        assert result["salary_currency"] == "USD"
        assert result["salary_min"] == 50000.0
        assert result["salary_max"] is None
