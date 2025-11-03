"""Shared test fixtures for job-agent-backend integration tests."""

import os
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.types import TypeDecorator, String

from jobs_repository.database.base import Base


class JSONArray(TypeDecorator):
    """Custom type that stores arrays as JSON in SQLite."""

    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Convert list to JSON string for storage."""
        if value is not None:
            import json

            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        """Convert JSON string back to list."""
        if value is not None:
            import json

            return json.loads(value)
        return value


@pytest.fixture
def in_memory_engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:", echo=False, connect_args={"check_same_thread": False}
    )

    # Remove schema from all tables for SQLite compatibility
    # and replace ARRAY types with JSONArray
    for table in Base.metadata.tables.values():
        table.schema = None
        for column in table.columns:
            if hasattr(column.type, "__class__") and column.type.__class__.__name__ == "ARRAY":
                # Replace PostgreSQL ARRAY with our JSONArray type for SQLite
                column.type = JSONArray()

    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(in_memory_engine) -> Generator[Session, None, None]:
    """Create a database session for testing."""
    SessionLocal = sessionmaker(bind=in_memory_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def temp_cv_dir():
    """Create a temporary directory for CV storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


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


@pytest.fixture
def mock_scrapper_manager():
    """Mock ScrapperManager for testing."""
    mock = MagicMock()
    mock.scrape_jobs_as_dicts.return_value = [
        {
            "job_id": 1,
            "title": "Python Developer",
            "url": "https://example.com/1",
            "description": "Python dev position",
            "company": {"name": "TechCo", "website": "https://techco.com"},
            "category": "Software Development",
            "date_posted": "2024-01-15T10:00:00Z",
            "valid_through": "2024-02-15T10:00:00Z",
            "employment_type": "FULL_TIME",
            "experience_months": 24.0,
            "location": {"region": "Remote", "is_remote": True, "can_apply": True},
            "industry": "Technology",
        }
    ]
    return mock


@pytest.fixture
def mock_openai_responses():
    """Mock OpenAI API responses for workflow testing."""

    def create_mock_response(content: str):
        """Create a mock OpenAI response."""
        mock_response = MagicMock()
        mock_response.content = content
        return mock_response

    return {
        "relevance_check": create_mock_response('{"is_relevant": true, "reasoning": "Good match"}'),
        "must_have_skills": create_mock_response('{"skills": ["Python", "Django", "PostgreSQL"]}'),
        "nice_to_have_skills": create_mock_response('{"skills": ["Docker", "Kubernetes"]}'),
        "pii_removal": create_mock_response(
            "Professional Experience:\n- 5+ years of Python development at [COMPANY]\n- Led team of engineers"
        ),
    }


@pytest.fixture
def sample_temp_cv_file(temp_cv_dir, sample_cv_content):
    """Create a temporary CV text file for testing."""
    cv_file = temp_cv_dir / "test_cv.txt"
    cv_file.write_text(sample_cv_content)
    return cv_file


@pytest.fixture
def sample_pdf_cv_path(temp_cv_dir):
    """Create a temporary PDF file path for testing (without actual PDF content)."""
    pdf_file = temp_cv_dir / "test_cv.pdf"
    return pdf_file


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Set up test environment variables."""
    # Disable LangSmith tracing for tests
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")
    # Set test OpenAI API key (tests should mock the actual API)
    if not os.getenv("OPENAI_API_KEY"):
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
