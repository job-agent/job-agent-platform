"""Tests for JobMapper class."""

from datetime import datetime

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

    def test_external_id_converts_to_string(self, mapper):
        """Test that job_id is converted to string for external_id."""
        job_data = {"job_id": 12345, "title": "Test"}

        result = mapper.map_to_model(job_data)

        assert result["external_id"] == "12345"
        assert isinstance(result["external_id"], str)

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

    def test_map_datetime_with_missing_dates(self, mapper):
        """Test mapping when datetime fields are missing."""
        job_data = {"job_id": 1, "title": "Test"}

        result = mapper.map_to_model(job_data)

        assert "posted_at" not in result
        assert "expires_at" not in result

    def test_empty_skills_arrays_are_mapped(self, mapper):
        """Test that empty skills arrays ARE included in mapping.

        Empty skill lists explicitly indicate "no skills found" which is
        semantically different from "skills not extracted" (None/missing).
        Empty lists SHOULD be mapped to preserve this distinction.
        """
        job_data = {
            "job_id": 1,
            "title": "Test",
            "must_have_skills": [],
            "nice_to_have_skills": [],
        }

        result = mapper.map_to_model(job_data)

        assert result["must_have_skills"] == []
        assert result["nice_to_have_skills"] == []

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

    def test_salary_with_partial_data(self, mapper):
        """Test salary mapping with only some fields."""
        job_data = {"job_id": 1, "title": "Test", "salary": {"min_value": 50000.0}}

        result = mapper.map_to_model(job_data)

        assert result["salary_currency"] == "USD"
        assert result["salary_min"] == 50000.0
        assert result["salary_max"] is None


class TestJobMapperIsRelevant:
    """Tests for JobMapper is_relevant field handling."""

    @pytest.fixture
    def mapper(self):
        """Create a JobMapper instance."""
        return JobMapper()

    def test_map_to_model_includes_is_relevant_true(self, mapper):
        """Test that is_relevant=True is included in mapped data."""
        job_data = {"job_id": 1, "title": "Test", "is_relevant": True}

        result = mapper.map_to_model(job_data)

        assert "is_relevant" in result
        assert result["is_relevant"] is True

    def test_map_to_model_includes_is_relevant_false(self, mapper):
        """Test that is_relevant=False is included in mapped data."""
        job_data = {"job_id": 1, "title": "Test", "is_relevant": False}

        result = mapper.map_to_model(job_data)

        assert "is_relevant" in result
        assert result["is_relevant"] is False

    def test_map_to_model_defaults_is_relevant_to_true(self, mapper):
        """Test that is_relevant defaults to True when not in input."""
        job_data = {"job_id": 1, "title": "Test"}

        result = mapper.map_to_model(job_data)

        assert "is_relevant" in result
        assert result["is_relevant"] is True

    def test_map_to_model_with_complete_data_includes_is_relevant(self, mapper):
        """Test that complete job data includes is_relevant field."""
        job_data = {
            "job_id": 12345,
            "title": "Senior Software Engineer",
            "description": "We are looking for an experienced engineer.",
            "company": {"name": "Tech Corp"},
            "is_relevant": False,
        }

        result = mapper.map_to_model(job_data)

        assert result["is_relevant"] is False


class TestJobMapperFromModelIsRelevant:
    """Tests for JobMapper.map_from_model is_relevant field handling."""

    @pytest.fixture
    def mapper(self):
        """Create a JobMapper instance."""
        return JobMapper()

    def test_map_from_model_includes_is_relevant_true(self, mapper, sample_job):
        """Test that is_relevant=True is included when serializing from model."""
        sample_job.is_relevant = True

        result = mapper.map_from_model(sample_job)

        assert "is_relevant" in result
        assert result["is_relevant"] is True

    def test_map_from_model_includes_is_relevant_false(self, mapper, sample_job):
        """Test that is_relevant=False is included when serializing from model."""
        sample_job.is_relevant = False

        result = mapper.map_from_model(sample_job)

        assert "is_relevant" in result
        assert result["is_relevant"] is False


class TestJobMapperIsFiltered:
    """Tests for JobMapper is_filtered field handling.

    These tests verify the NEW behavior where is_filtered field is mapped
    correctly between JobDict contract data and Job model format.
    """

    @pytest.fixture
    def mapper(self):
        """Create a JobMapper instance."""
        return JobMapper()

    def test_map_to_model_includes_is_filtered_true(self, mapper):
        """Test that is_filtered=True is included in mapped data."""
        job_data = {"job_id": 1, "title": "Test", "is_filtered": True}

        result = mapper.map_to_model(job_data)

        assert "is_filtered" in result
        assert result["is_filtered"] is True

    def test_map_to_model_includes_is_filtered_false(self, mapper):
        """Test that is_filtered=False is included in mapped data."""
        job_data = {"job_id": 1, "title": "Test", "is_filtered": False}

        result = mapper.map_to_model(job_data)

        assert "is_filtered" in result
        assert result["is_filtered"] is False

    def test_map_to_model_defaults_is_filtered_to_false(self, mapper):
        """Test that is_filtered defaults to False when not in input.

        Jobs should default to not being filtered.
        """
        job_data = {"job_id": 1, "title": "Test"}

        result = mapper.map_to_model(job_data)

        assert "is_filtered" in result
        assert result["is_filtered"] is False

    def test_map_to_model_with_complete_data_includes_is_filtered(self, mapper):
        """Test that complete job data includes is_filtered field."""
        job_data = {
            "job_id": 12345,
            "title": "Senior Software Engineer",
            "description": "We are looking for an experienced engineer.",
            "company": {"name": "Tech Corp"},
            "is_filtered": True,
            "is_relevant": False,
        }

        result = mapper.map_to_model(job_data)

        assert result["is_filtered"] is True
        assert result["is_relevant"] is False


class TestJobMapperFromModelIsFiltered:
    """Tests for JobMapper.map_from_model is_filtered field handling."""

    @pytest.fixture
    def mapper(self):
        """Create a JobMapper instance."""
        return JobMapper()

    def test_map_from_model_includes_is_filtered_true(self, mapper, sample_job):
        """Test that is_filtered=True is included when serializing from model."""
        sample_job.is_filtered = True

        result = mapper.map_from_model(sample_job)

        assert "is_filtered" in result
        assert result["is_filtered"] is True

    def test_map_from_model_includes_is_filtered_false(self, mapper, sample_job):
        """Test that is_filtered=False is included when serializing from model."""
        sample_job.is_filtered = False

        result = mapper.map_from_model(sample_job)

        assert "is_filtered" in result
        assert result["is_filtered"] is False

    def test_map_from_model_filtered_job_has_correct_flags(self, mapper, sample_job):
        """Test that a filtered job is serialized with correct flags."""
        sample_job.is_filtered = True
        sample_job.is_relevant = False

        result = mapper.map_from_model(sample_job)

        assert result["is_filtered"] is True
        assert result["is_relevant"] is False


class TestJobMapperWith2DSkillStructure:
    """Tests for JobMapper with 2D skill structure.

    These tests verify the new behavior where skills are stored as 2D lists:
    - Outer list: AND relationships (all groups required)
    - Inner lists: OR relationships (alternatives within a group)
    """

    @pytest.fixture
    def mapper(self):
        """Create a JobMapper instance."""
        return JobMapper()

    def test_map_to_model_accepts_2d_skill_lists(self, mapper):
        """Test that map_to_model accepts 2D skill lists."""
        job_data = {
            "job_id": 1,
            "title": "Test",
            "must_have_skills": [["Python"], ["Django"], ["PostgreSQL"]],
            "nice_to_have_skills": [["Docker"], ["AWS"]],
        }

        result = mapper.map_to_model(job_data)

        assert result["must_have_skills"] == [["Python"], ["Django"], ["PostgreSQL"]]
        assert result["nice_to_have_skills"] == [["Docker"], ["AWS"]]

    def test_map_to_model_accepts_or_groups(self, mapper):
        """Test that map_to_model accepts OR groups in inner lists."""
        job_data = {
            "job_id": 1,
            "title": "Test",
            "must_have_skills": [["JavaScript", "Python"], ["React"]],
            "nice_to_have_skills": [["AWS", "GCP"], ["Docker"]],
        }

        result = mapper.map_to_model(job_data)

        assert result["must_have_skills"] == [["JavaScript", "Python"], ["React"]]
        assert result["nice_to_have_skills"] == [["AWS", "GCP"], ["Docker"]]

    def test_map_to_model_accepts_mixed_solo_and_or_groups(self, mapper):
        """Test that map_to_model accepts mix of solo skills and OR groups."""
        job_data = {
            "job_id": 1,
            "title": "Test",
            "must_have_skills": [
                ["JavaScript", "TypeScript"],
                ["React"],
                ["PostgreSQL", "MySQL"],
            ],
            "nice_to_have_skills": [],
        }

        result = mapper.map_to_model(job_data)

        assert result["must_have_skills"] == [
            ["JavaScript", "TypeScript"],
            ["React"],
            ["PostgreSQL", "MySQL"],
        ]

    def test_map_to_model_accepts_empty_2d_skill_list(self, mapper):
        """Test that map_to_model accepts empty 2D skill list."""
        job_data = {
            "job_id": 1,
            "title": "Test",
            "must_have_skills": [],
            "nice_to_have_skills": [],
        }

        result = mapper.map_to_model(job_data)

        assert result["must_have_skills"] == []
        assert result["nice_to_have_skills"] == []

    def test_map_to_model_preserves_skill_order(self, mapper):
        """Test that map_to_model preserves order of skill groups."""
        job_data = {
            "job_id": 1,
            "title": "Test",
            "must_have_skills": [["A"], ["B", "C"], ["D"]],
            "nice_to_have_skills": [],
        }

        result = mapper.map_to_model(job_data)

        assert result["must_have_skills"] == [["A"], ["B", "C"], ["D"]]

    def test_map_to_model_preserves_alternatives_order(self, mapper):
        """Test that map_to_model preserves order of alternatives within groups."""
        job_data = {
            "job_id": 1,
            "title": "Test",
            "must_have_skills": [["JavaScript", "TypeScript", "Python"]],
            "nice_to_have_skills": [],
        }

        result = mapper.map_to_model(job_data)

        assert result["must_have_skills"][0] == ["JavaScript", "TypeScript", "Python"]

    def test_map_from_model_returns_2d_skill_lists(self, mapper, sample_job):
        """Test that map_from_model returns 2D skill lists."""
        sample_job.must_have_skills = [["Python"], ["Django"]]
        sample_job.nice_to_have_skills = [["Docker", "Kubernetes"]]

        result = mapper.map_from_model(sample_job)

        assert result["must_have_skills"] == [["Python"], ["Django"]]
        assert result["nice_to_have_skills"] == [["Docker", "Kubernetes"]]

    def test_map_from_model_returns_empty_2d_list(self, mapper, sample_job):
        """Test that map_from_model returns empty 2D list when no skills."""
        sample_job.must_have_skills = []
        sample_job.nice_to_have_skills = []

        result = mapper.map_from_model(sample_job)

        assert result["must_have_skills"] == []
        assert result["nice_to_have_skills"] == []

    def test_map_to_model_skills_with_special_characters(self, mapper):
        """Test that skills with special characters are preserved."""
        job_data = {
            "job_id": 1,
            "title": "Test",
            "must_have_skills": [["C++", "C#"], ["Node.js"], ["AWS/GCP"]],
            "nice_to_have_skills": [],
        }

        result = mapper.map_to_model(job_data)

        assert result["must_have_skills"] == [["C++", "C#"], ["Node.js"], ["AWS/GCP"]]

    def test_complete_job_dict_with_2d_skills(self, mapper):
        """Test mapping complete job data with 2D skill structure."""
        job_data = {
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
            "must_have_skills": [["Python", "Java"], ["Django"], ["PostgreSQL", "MySQL"]],
            "nice_to_have_skills": [["Docker", "Kubernetes"], ["AWS"]],
        }

        result = mapper.map_to_model(job_data)

        assert result["must_have_skills"] == [
            ["Python", "Java"],
            ["Django"],
            ["PostgreSQL", "MySQL"],
        ]
        assert result["nice_to_have_skills"] == [["Docker", "Kubernetes"], ["AWS"]]
        assert result["title"] == "Senior Software Engineer"
        assert result["external_id"] == "12345"
