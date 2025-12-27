"""Test fixtures for core module tests."""

from pathlib import Path
from typing import Optional
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from dependency_injector import providers

from job_agent_backend.container import ApplicationContainer
from job_agent_backend.filter_service.filter import FilterService


class StubJobRepository:
    """Stub job repository for testing orchestrator.

    This stub provides minimal implementations of IJobRepository methods
    that are used by the orchestrator and filter service during tests.
    """

    def __init__(self):
        self.saved_filtered_jobs: list = []
        self.latest_updated_at: Optional[datetime] = None

    def get_by_external_id(self, external_id, source=None):
        return None

    def has_active_job_with_title_and_company(self, title, company_name):
        return False

    def save_filtered_jobs(self, jobs):
        self.saved_filtered_jobs.extend(jobs)
        return len(jobs)

    def get_latest_updated_at(self):
        return self.latest_updated_at


@pytest.fixture
def stub_job_repository():
    """Create a fresh StubJobRepository instance for testing."""
    return StubJobRepository()


@pytest.fixture
def app_container_with_stub_repository(stub_job_repository):
    """Provide an ApplicationContainer configured with a stub job repository.

    This fixture creates an ApplicationContainer with the job_repository_factory
    and filter_service overridden to use the stub repository. Test classes can
    use this instead of creating their own container configuration.
    """
    container = ApplicationContainer()
    container.job_repository_factory.override(providers.Object(lambda: stub_job_repository))
    container.filter_service.override(
        providers.Singleton(
            FilterService,
            job_repository_factory=container.job_repository_factory,
        )
    )
    return container


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
def temp_cv_dir(tmp_path):
    """Create a temporary directory for CV files."""
    cv_dir = tmp_path / "cv_files"
    cv_dir.mkdir()
    return Path(cv_dir)


@pytest.fixture
def sample_temp_cv_file(temp_cv_dir, sample_cv_content):
    """Create a temporary CV text file for testing."""
    cv_file = temp_cv_dir / "test_cv.txt"
    cv_file.write_text(sample_cv_content)
    return cv_file
