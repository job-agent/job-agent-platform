"""Test fixtures for filter service tests."""

import pytest


@pytest.fixture
def sample_job_dict():
    """Sample JobDict for testing."""
    return {
        "job_id": 12345,
        "title": "Senior Python Developer",
        "url": "https://example.com/jobs/12345",
        "description": """
        We are looking for a Senior Python Developer with strong experience in:
        - Python (5+ years required)
        - Django or Flask
        - PostgreSQL
        - Docker and Kubernetes (nice to have)
        - RESTful API design

        Responsibilities:
        - Design and implement backend services
        - Mentor junior developers
        - Participate in code reviews
        """,
        "company": {"name": "Example Corp", "website": "https://example.com"},
        "category": "Software Development",
        "date_posted": "2024-01-15T10:00:00Z",
        "valid_through": "2024-02-15T10:00:00Z",
        "employment_type": "FULL_TIME",
        "salary": {"currency": "USD", "min_value": 120000.0, "max_value": 160000.0},
        "experience_months": 36.0,
        "location": {"region": "New York, NY", "is_remote": True, "can_apply": True},
        "industry": "Information Technology",
    }


@pytest.fixture
def sample_jobs_list():
    """Sample list of jobs for filtering tests."""
    return [
        {
            "job_id": 1,
            "title": "Junior Developer",
            "experience_months": 12,
            "location": {"region": "Remote", "can_apply": True},
        },
        {
            "job_id": 2,
            "title": "Mid-level Developer",
            "experience_months": 36,
            "location": {"region": "New York", "can_apply": True},
        },
        {
            "job_id": 3,
            "title": "Senior Developer",
            "experience_months": 60,
            "location": {"region": "San Francisco", "can_apply": False},
        },
        {
            "job_id": 4,
            "title": "Staff Engineer",
            "experience_months": 96,
            "location": {"region": "Austin", "can_apply": True},
        },
    ]
