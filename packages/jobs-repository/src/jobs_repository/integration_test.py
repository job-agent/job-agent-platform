"""Integration tests for jobs-repository package.

These tests verify end-to-end functionality combining multiple components:
- JobMapper: Maps contract data to model format
- JobRepository: Persists jobs and manages reference data
- ReferenceDataService: Manages reference entities (company, location, etc.)
- Database models: Job, Company, Location, Category, Industry
"""

from datetime import datetime, timedelta, UTC

import pytest
from sqlalchemy.orm import sessionmaker

from jobs_repository.repository import JobRepository
from jobs_repository.models import Company, Location, Category, Industry


class TestJobCreationFlow:
    """End-to-end tests for job creation flow."""

    @pytest.fixture
    def repository(self, reference_data_service, job_mapper, db_session):
        """Create a JobRepository instance."""
        return JobRepository(reference_data_service, job_mapper, db_session)

    def test_complete_job_creation_and_retrieval(self, repository, db_session):
        """Test complete flow: create job with all data and retrieve it."""
        job_data = {
            "job_id": 10001,
            "title": "Senior Software Engineer",
            "url": "https://company.com/jobs/10001",
            "description": "We are looking for a senior software engineer.",
            "company": {"name": "Integration Test Corp", "website": "https://test.com"},
            "category": "Software Engineering",
            "industry": "Information Technology",
            "location": {"region": "New York, NY", "is_remote": True},
            "employment_type": "FULL_TIME",
            "experience_months": 48.0,
            "salary": {"currency": "USD", "min_value": 150000.0, "max_value": 200000.0},
            "date_posted": "2024-01-15T10:00:00Z",
            "valid_through": "2024-03-15T10:00:00Z",
            "must_have_skills": ["Python", "PostgreSQL", "Docker"],
            "nice_to_have_skills": ["Kubernetes", "AWS"],
        }

        created_job = repository.create(job_data)

        assert created_job.id is not None
        assert created_job.title == "Senior Software Engineer"
        assert created_job.external_id == "10001"
        assert created_job.source_url == "https://company.com/jobs/10001"
        assert created_job.description == "We are looking for a senior software engineer."
        assert created_job.job_type == "FULL_TIME"
        assert created_job.experience_months == 48.0
        assert created_job.salary_min == 150000.0
        assert created_job.salary_max == 200000.0
        assert created_job.salary_currency == "USD"
        assert created_job.is_remote is True
        assert created_job.must_have_skills == ["Python", "PostgreSQL", "Docker"]
        assert created_job.nice_to_have_skills == ["Kubernetes", "AWS"]

        assert created_job.company_rel.name == "Integration Test Corp"
        assert created_job.location_rel.region == "New York, NY"
        assert created_job.category_rel.name == "Software Engineering"
        assert created_job.industry_rel.name == "Information Technology"

        retrieved_job = repository.get_by_external_id("10001")
        assert retrieved_job is not None
        assert retrieved_job.id == created_job.id
        assert retrieved_job.title == created_job.title
        assert retrieved_job.company_rel.name == "Integration Test Corp"

    def test_reference_data_reuse_across_multiple_jobs(self, repository, db_session):
        """Test that reference entities are reused when creating multiple jobs."""
        job_data_1 = {
            "job_id": 20001,
            "title": "Backend Developer",
            "company": {"name": "Shared Company"},
            "category": "Engineering",
            "industry": "Tech",
            "location": {"region": "San Francisco, CA"},
        }

        job_data_2 = {
            "job_id": 20002,
            "title": "Frontend Developer",
            "company": {"name": "Shared Company"},
            "category": "Engineering",
            "industry": "Tech",
            "location": {"region": "San Francisco, CA"},
        }

        job1 = repository.create(job_data_1)
        job2 = repository.create(job_data_2)

        assert job1.company_id == job2.company_id
        assert job1.category_id == job2.category_id
        assert job1.industry_id == job2.industry_id
        assert job1.location_id == job2.location_id

        assert db_session.query(Company).filter_by(name="Shared Company").count() == 1
        assert db_session.query(Category).filter_by(name="Engineering").count() == 1
        assert db_session.query(Industry).filter_by(name="Tech").count() == 1
        assert db_session.query(Location).filter_by(region="San Francisco, CA").count() == 1


class TestJobMapperRepositoryIntegration:
    """Tests for mapper and repository integration."""

    @pytest.fixture
    def repository(self, reference_data_service, job_mapper, db_session):
        """Create a JobRepository instance."""
        return JobRepository(reference_data_service, job_mapper, db_session)

    def test_mapper_transforms_job_id_to_external_id(self, repository):
        """Test that job_id is correctly mapped to external_id."""
        job_data = {"job_id": 99999, "title": "Mapper Test Job"}

        job = repository.create(job_data)

        assert job.external_id == "99999"

    def test_mapper_transforms_url_to_source_url(self, repository):
        """Test that url is correctly mapped to source_url."""
        job_data = {
            "job_id": 88888,
            "title": "URL Test Job",
            "url": "https://original-url.com/job/88888",
        }

        job = repository.create(job_data)

        assert job.source_url == "https://original-url.com/job/88888"

    def test_mapper_transforms_employment_type_to_job_type(self, repository):
        """Test that employment_type is correctly mapped to job_type."""
        job_data = {"job_id": 77777, "title": "Type Test Job", "employment_type": "CONTRACT"}

        job = repository.create(job_data)

        assert job.job_type == "CONTRACT"

    def test_mapper_extracts_salary_fields(self, repository):
        """Test that salary object is correctly extracted to individual fields."""
        job_data = {
            "job_id": 66666,
            "title": "Salary Test Job",
            "salary": {"currency": "EUR", "min_value": 80000.0, "max_value": 120000.0},
        }

        job = repository.create(job_data)

        assert job.salary_currency == "EUR"
        assert job.salary_min == 80000.0
        assert job.salary_max == 120000.0

    def test_mapper_extracts_location_fields(self, repository):
        """Test that location object is correctly extracted."""
        job_data = {
            "job_id": 55555,
            "title": "Location Test Job",
            "location": {"region": "London, UK", "is_remote": True},
        }

        job = repository.create(job_data)

        assert job.location_rel.region == "London, UK"
        assert job.is_remote is True

    def test_mapper_parses_datetime_fields(self, repository):
        """Test that datetime strings are correctly parsed."""
        job_data = {
            "job_id": 44444,
            "title": "DateTime Test Job",
            "date_posted": "2024-06-15T14:30:00Z",
            "valid_through": "2024-09-15T23:59:59Z",
        }

        job = repository.create(job_data)

        assert job.posted_at is not None
        assert job.expires_at is not None
        assert job.posted_at.year == 2024
        assert job.posted_at.month == 6
        assert job.posted_at.day == 15


class TestSessionFactoryIntegration:
    """Tests for repository with session factory."""

    def test_repository_manages_own_sessions(
        self, reference_data_service, job_mapper, in_memory_engine
    ):
        """Test that repository can manage its own sessions with factory."""
        factory = sessionmaker(bind=in_memory_engine)
        repository = JobRepository(reference_data_service, job_mapper, session_factory=factory)

        job_data = {"job_id": 33333, "title": "Factory Session Job"}
        job = repository.create(job_data)

        assert job.id is not None

        retrieved = repository.get_by_external_id("33333")
        assert retrieved is not None
        assert retrieved.title == "Factory Session Job"

    def test_multiple_operations_with_session_factory(
        self, reference_data_service, job_mapper, in_memory_engine
    ):
        """Test multiple operations work correctly with session factory."""
        factory = sessionmaker(bind=in_memory_engine)
        repository = JobRepository(reference_data_service, job_mapper, session_factory=factory)

        job1 = repository.create({"job_id": 11111, "title": "Job 1"})
        job2 = repository.create({"job_id": 22222, "title": "Job 2"})

        retrieved1 = repository.get_by_external_id("11111")
        retrieved2 = repository.get_by_external_id("22222")

        assert retrieved1.id == job1.id
        assert retrieved2.id == job2.id


class TestActiveJobQueries:
    """Tests for active job query methods."""

    @pytest.fixture
    def repository(self, reference_data_service, job_mapper, db_session):
        """Create a JobRepository instance."""
        return JobRepository(reference_data_service, job_mapper, db_session)

    def test_has_active_job_integration(self, repository, reference_data_service, db_session):
        """Test has_active_job_with_title_and_company in full flow."""
        job_data = {
            "job_id": 90001,
            "title": "Active Job Check",
            "company": {"name": "Active Check Corp"},
            "valid_through": (datetime.now(UTC) + timedelta(days=30)).isoformat(),
        }

        repository.create(job_data)

        assert repository.has_active_job_with_title_and_company(
            "Active Job Check", "Active Check Corp"
        )

        assert not repository.has_active_job_with_title_and_company(
            "Different Title", "Active Check Corp"
        )

    def test_get_existing_urls_integration(self, repository, db_session):
        """Test get_existing_urls_by_source in full flow."""
        now = datetime.now(UTC)
        posted_at_str = now.isoformat()

        job_data_1 = {
            "job_id": 80001,
            "title": "URL Query Job 1",
            "url": "https://source.com/jobs/80001",
            "date_posted": posted_at_str,
        }
        job_data_2 = {
            "job_id": 80002,
            "title": "URL Query Job 2",
            "url": "https://source.com/jobs/80002",
            "date_posted": posted_at_str,
        }

        repository.create(job_data_1)
        repository.create(job_data_2)

        urls = repository.get_existing_urls_by_source(source=None)

        assert len(urls) >= 2
        assert "https://source.com/jobs/80001" in urls
        assert "https://source.com/jobs/80002" in urls


class TestDataIntegrityAcrossComponents:
    """Tests for data integrity across all components."""

    @pytest.fixture
    def repository(self, reference_data_service, job_mapper, db_session):
        """Create a JobRepository instance."""
        return JobRepository(reference_data_service, job_mapper, db_session)

    def test_special_characters_preserved_through_pipeline(self, repository):
        """Test that special characters are preserved through the entire pipeline."""
        job_data = {
            "job_id": 70001,
            "title": "C++ & Python Developer (Senior) - Remote",
            "description": "Looking for devs with <5 years exp. Salary > $100k",
            "company": {"name": "Tech & Data Corp."},
            "category": "Software Development & Engineering",
            "location": {"region": "São Paulo, Brazil"},
        }

        job = repository.create(job_data)

        assert job.title == "C++ & Python Developer (Senior) - Remote"
        assert "<5" in job.description
        assert ">" in job.description
        assert job.company_rel.name == "Tech & Data Corp."
        assert job.category_rel.name == "Software Development & Engineering"
        assert job.location_rel.region == "São Paulo, Brazil"

    def test_unicode_preserved_through_pipeline(self, repository):
        """Test that unicode characters are preserved through the entire pipeline."""
        job_data = {
            "job_id": 70002,
            "title": "ソフトウェアエンジニア",
            "description": "日本語の求人説明です。",
            "company": {"name": "株式会社テック"},
            "location": {"region": "東京, 日本"},
        }

        job = repository.create(job_data)

        assert job.title == "ソフトウェアエンジニア"
        assert job.description == "日本語の求人説明です。"
        assert job.company_rel.name == "株式会社テック"
        assert job.location_rel.region == "東京, 日本"

    def test_large_skills_arrays_preserved(self, repository):
        """Test that large skills arrays are preserved correctly."""
        many_skills = [f"Skill{i}" for i in range(50)]

        job_data = {
            "job_id": 70003,
            "title": "Multi-Skill Job",
            "must_have_skills": many_skills[:25],
            "nice_to_have_skills": many_skills[25:],
        }

        job = repository.create(job_data)

        assert len(job.must_have_skills) == 25
        assert len(job.nice_to_have_skills) == 25
        assert job.must_have_skills[0] == "Skill0"
        assert job.nice_to_have_skills[-1] == "Skill49"
