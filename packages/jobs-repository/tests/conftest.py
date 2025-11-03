"""Shared test fixtures for jobs-repository tests."""

from datetime import datetime, UTC
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.types import TypeDecorator, String

from jobs_repository.database.base import Base
from jobs_repository.models import Job, Company, Location, Category, Industry


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
def sample_company(db_session) -> Company:
    """Create a sample company for testing."""
    company = Company(name="Tech Corp", website="https://techcorp.com")
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


@pytest.fixture
def sample_location(db_session) -> Location:
    """Create a sample location for testing."""
    location = Location(region="San Francisco, CA")
    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)
    return location


@pytest.fixture
def sample_category(db_session) -> Category:
    """Create a sample category for testing."""
    category = Category(name="Software Engineering")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def sample_industry(db_session) -> Industry:
    """Create a sample industry for testing."""
    industry = Industry(name="Technology")
    db_session.add(industry)
    db_session.commit()
    db_session.refresh(industry)
    return industry


@pytest.fixture
def sample_job(
    db_session, sample_company, sample_location, sample_category, sample_industry
) -> Job:
    """Create a sample job for testing."""
    job = Job(
        title="Software Engineer",
        description="We are looking for a talented software engineer.",
        must_have_skills=["Python", "SQL"],
        nice_to_have_skills=["Docker", "Kubernetes"],
        company_id=sample_company.id,
        location_id=sample_location.id,
        category_id=sample_category.id,
        industry_id=sample_industry.id,
        job_type="Full-time",
        experience_months=24,
        salary_min=100000.0,
        salary_max=150000.0,
        salary_currency="USD",
        external_id="job-123",
        source="LinkedIn",
        source_url="https://linkedin.com/jobs/123",
        is_remote=False,
        posted_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
        expires_at=datetime(2024, 2, 1, 12, 0, 0, tzinfo=UTC),
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


@pytest.fixture
def sample_job_dict():
    """Sample JobDict data for testing mapper and repository."""
    return {
        "job_id": 12345,
        "title": "Senior Python Developer",
        "url": "https://example.com/jobs/12345",
        "description": "Looking for an experienced Python developer.",
        "company": {"name": "Example Corp", "website": "https://example.com"},
        "category": "Software Development",
        "date_posted": "2024-01-15T10:00:00Z",
        "valid_through": "2024-02-15T10:00:00Z",
        "employment_type": "FULL_TIME",
        "salary": {"currency": "USD", "min_value": 120000.0, "max_value": 160000.0},
        "experience_months": 36.0,
        "location": {"region": "New York, NY", "is_remote": True},
        "industry": "Information Technology",
    }


@pytest.fixture
def sample_job_create_dict():
    """Sample JobCreate data with additional skills fields."""
    return {
        "job_id": 54321,
        "title": "DevOps Engineer",
        "url": "https://example.com/jobs/54321",
        "description": "We need a skilled DevOps engineer.",
        "company": {"name": "DevOps Inc", "website": "https://devopsinc.com"},
        "category": "DevOps",
        "date_posted": "2024-01-20T09:00:00Z",
        "valid_through": "2024-03-20T09:00:00Z",
        "employment_type": "CONTRACT",
        "experience_months": 48.0,
        "location": {"region": "Remote", "is_remote": True},
        "industry": "Cloud Computing",
        "must_have_skills": ["AWS", "Terraform", "Docker", "Kubernetes"],
        "nice_to_have_skills": ["Ansible", "Jenkins", "Python"],
    }
