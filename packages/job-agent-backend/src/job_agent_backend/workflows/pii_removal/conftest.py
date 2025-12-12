"""Test fixtures for PII removal workflow tests."""

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
def sample_cv_with_pii():
    """Sample CV with PII for testing PII removal."""
    return """
    John Doe
    Email: john.doe@example.com
    Phone: +1-555-123-4567
    Address: 123 Main St, San Francisco, CA 94105

    Professional Experience:
    - 5+ years of Python development at TechCorp
    - Led team of 10 engineers
    """
