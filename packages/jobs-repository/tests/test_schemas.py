"""Tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError
from jobs_repository.schemas import JobCreate, JobUpdate, JobSearch


def test_job_create_minimal():
    """Test creating a job with minimal required fields."""
    job = JobCreate(title="Software Engineer", company="Tech Corp")
    assert job.title == "Software Engineer"
    assert job.company == "Tech Corp"
    assert job.is_active is True
    assert job.is_remote is False


def test_job_create_with_all_fields():
    """Test creating a job with all fields."""
    job = JobCreate(
        title="Senior Software Engineer",
        company="Tech Corp",
        location="San Francisco",
        description="Great opportunity",
        job_type="Full-time",
        experience_level="Senior",
        salary_min=120000.0,
        salary_max=180000.0,
        salary_currency="USD",
        external_id="job-123",
        source="LinkedIn",
        source_url="https://example.com/job/123",
        is_active=True,
        is_remote=True,
    )
    assert job.salary_min == 120000.0
    assert job.salary_max == 180000.0


def test_job_create_salary_validation():
    """Test salary range validation."""
    with pytest.raises(ValidationError) as exc_info:
        JobCreate(
            title="Software Engineer",
            company="Tech Corp",
            salary_min=150000.0,
            salary_max=100000.0,  # Invalid: max < min
        )
    assert "salary_max must be greater than or equal to salary_min" in str(exc_info.value)


def test_job_create_negative_salary():
    """Test that negative salaries are rejected."""
    with pytest.raises(ValidationError):
        JobCreate(
            title="Software Engineer",
            company="Tech Corp",
            salary_min=-1000.0,
        )


def test_job_update():
    """Test JobUpdate schema."""
    update = JobUpdate(title="New Title", salary_max=200000.0)
    assert update.title == "New Title"
    assert update.salary_max == 200000.0


def test_job_search_defaults():
    """Test JobSearch schema with defaults."""
    search = JobSearch()
    assert search.skip == 0
    assert search.limit == 100
    assert search.is_active is True
    assert search.order_by == "created_at"
    assert search.order_desc is True


def test_job_search_with_filters():
    """Test JobSearch schema with filters."""
    search = JobSearch(
        query_text="Python",
        is_remote=True,
        company="Tech",
        skip=10,
        limit=50,
    )
    assert search.query_text == "Python"
    assert search.is_remote is True
    assert search.company == "Tech"
    assert search.skip == 10
    assert search.limit == 50


def test_job_search_limit_validation():
    """Test that limit is constrained."""
    with pytest.raises(ValidationError):
        JobSearch(limit=2000)  # Exceeds max of 1000
