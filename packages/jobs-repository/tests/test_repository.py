"""Tests for JobRepository."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jobs_repository.database import Base
from jobs_repository.repository import JobRepository


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def job_repo(in_memory_db):
    """Create a JobRepository instance with in-memory database."""
    return JobRepository(in_memory_db)


@pytest.fixture
def sample_job_data():
    """Sample job data for testing."""
    return {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "location": "San Francisco, CA",
        "description": "We are looking for a talented software engineer.",
        "job_type": "Full-time",
        "experience_level": "Mid",
        "salary_min": 100000.0,
        "salary_max": 150000.0,
        "external_id": "job-123",
        "source": "LinkedIn",
        "is_active": True,
        "is_remote": False,
    }


def test_create_job(job_repo, sample_job_data):
    """Test creating a new job."""
    job = job_repo.create(sample_job_data)

    assert job.id is not None
    assert job.title == sample_job_data["title"]
    assert job.company == sample_job_data["company"]
    assert job.external_id == sample_job_data["external_id"]


def test_get_by_id(job_repo, sample_job_data):
    """Test retrieving a job by ID."""
    created_job = job_repo.create(sample_job_data)
    retrieved_job = job_repo.get_by_id(created_job.id)

    assert retrieved_job is not None
    assert retrieved_job.id == created_job.id
    assert retrieved_job.title == created_job.title


def test_get_by_external_id(job_repo, sample_job_data):
    """Test retrieving a job by external ID."""
    job_repo.create(sample_job_data)
    retrieved_job = job_repo.get_by_external_id("job-123", "LinkedIn")

    assert retrieved_job is not None
    assert retrieved_job.external_id == "job-123"
    assert retrieved_job.source == "LinkedIn"


def test_get_all(job_repo, sample_job_data):
    """Test retrieving all jobs."""
    # Create multiple jobs
    for i in range(5):
        data = sample_job_data.copy()
        data["external_id"] = f"job-{i}"
        job_repo.create(data)

    jobs = job_repo.get_all(limit=10)
    assert len(jobs) == 5


def test_search_by_title(job_repo, sample_job_data):
    """Test searching jobs by title."""
    job_repo.create(sample_job_data)

    # Create another job with different title and description
    other_data = sample_job_data.copy()
    other_data["title"] = "Data Scientist"
    other_data["description"] = "We are looking for a talented data scientist."
    other_data["external_id"] = "job-456"
    job_repo.create(other_data)

    results = job_repo.search(query_text="Software")
    assert len(results) == 1
    assert results[0].title == "Software Engineer"


def test_update_job(job_repo, sample_job_data):
    """Test updating a job."""
    job = job_repo.create(sample_job_data)
    updated_job = job_repo.update(job.id, {"title": "Senior Software Engineer"})

    assert updated_job is not None
    assert updated_job.title == "Senior Software Engineer"


def test_delete_job(job_repo, sample_job_data):
    """Test deleting a job."""
    job = job_repo.create(sample_job_data)
    result = job_repo.delete(job.id)

    assert result is True
    assert job_repo.get_by_id(job.id) is None


def test_soft_delete_job(job_repo, sample_job_data):
    """Test soft deleting a job."""
    job = job_repo.create(sample_job_data)
    updated_job = job_repo.soft_delete(job.id)

    assert updated_job is not None
    assert updated_job.is_active is False


def test_bulk_create(job_repo, sample_job_data):
    """Test bulk creating jobs."""
    jobs_data = []
    for i in range(3):
        data = sample_job_data.copy()
        data["external_id"] = f"job-bulk-{i}"
        jobs_data.append(data)

    jobs = job_repo.bulk_create(jobs_data)
    assert len(jobs) == 3


def test_count(job_repo, sample_job_data):
    """Test counting jobs."""
    # Create active jobs
    for i in range(3):
        data = sample_job_data.copy()
        data["external_id"] = f"job-active-{i}"
        job_repo.create(data)

    # Create inactive job
    inactive_data = sample_job_data.copy()
    inactive_data["external_id"] = "job-inactive"
    inactive_data["is_active"] = False
    job_repo.create(inactive_data)

    total_count = job_repo.count()
    active_count = job_repo.count(is_active=True)
    inactive_count = job_repo.count(is_active=False)

    assert total_count == 4
    assert active_count == 3
    assert inactive_count == 1


def test_upsert_creates_new(job_repo, sample_job_data):
    """Test upsert creates a new job when it doesn't exist."""
    job = job_repo.upsert("new-job-123", "LinkedIn", sample_job_data)

    assert job.id is not None
    assert job.external_id == "new-job-123"


def test_upsert_updates_existing(job_repo, sample_job_data):
    """Test upsert updates an existing job."""
    # Create initial job
    job_repo.create(sample_job_data)

    # Upsert with updated data
    updated_data = sample_job_data.copy()
    updated_data["title"] = "Updated Title"
    updated_job = job_repo.upsert("job-123", "LinkedIn", updated_data)

    assert updated_job.title == "Updated Title"
    assert job_repo.count() == 1  # Should still be only one job
