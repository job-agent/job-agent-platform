"""Test fixtures for job processing workflow tests."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def sample_cv_content():
    """Sample CV content for testing."""
    return """
    Professional Experience:
    - 5+ years of Python development
    - Expertise in Django, Flask, FastAPI
    - Experience with PostgreSQL and MongoDB
    - Strong background in RESTful API design
    - Proficient in Docker and Kubernetes

    Skills:
    - Languages: Python, JavaScript, SQL
    - Frameworks: Django, React
    - Tools: Git, Docker, Jenkins
    """


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
def sample_irrelevant_job_dict():
    """Sample irrelevant JobDict for testing."""
    return {
        "job_id": 67890,
        "title": "Senior Java Architect",
        "url": "https://example.com/jobs/67890",
        "description": """
        We are looking for a Senior Java Architect with:
        - 10+ years of Java/J2EE experience (required)
        - Spring Boot, Hibernate
        - Microservices architecture
        - AWS or Azure cloud experience

        No Python experience needed.
        """,
        "company": {"name": "Java Corp", "website": "https://javacorp.com"},
        "category": "Software Architecture",
        "date_posted": "2024-01-16T10:00:00Z",
        "valid_through": "2024-02-16T10:00:00Z",
        "employment_type": "FULL_TIME",
        "salary": {"currency": "USD", "min_value": 150000.0, "max_value": 200000.0},
        "experience_months": 120.0,
        "location": {"region": "Seattle, WA", "is_remote": False, "can_apply": True},
        "industry": "Enterprise Software",
    }


@pytest.fixture
def job_repository_factory_stub():
    """Provide a stub job repository factory."""

    def factory():
        repository = MagicMock()
        repository.create.return_value = MagicMock(id=1)
        return repository

    return factory
