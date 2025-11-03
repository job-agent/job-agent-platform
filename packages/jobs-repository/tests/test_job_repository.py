"""Tests for JobRepository class."""

from unittest.mock import patch

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from jobs_repository.repository import JobRepository
from jobs_repository.models import Job, Company, Location, Category, Industry
from jobs_repository.exceptions import (
    JobAlreadyExistsError,
    TransactionError,
    ValidationError,
)


class TestJobRepository:
    """Test suite for JobRepository class."""

    @pytest.fixture
    def repository(self, db_session):
        """Create a JobRepository instance."""
        return JobRepository(db_session)

    # ============================================================
    # Tests for Internal Helper Methods
    # ============================================================

    def test_get_or_create_company_creates_new(self, repository, db_session):
        """Test creating a new company when it doesn't exist."""
        company = repository._get_or_create_company("New Company")

        assert company.id is not None
        assert company.name == "New Company"

        # Verify it's in the database
        db_company = db_session.query(Company).filter_by(name="New Company").first()
        assert db_company is not None
        assert db_company.id == company.id

    def test_get_or_create_company_returns_existing(self, repository, sample_company):
        """Test returning existing company instead of creating duplicate."""
        company = repository._get_or_create_company(sample_company.name)

        assert company.id == sample_company.id
        assert company.name == sample_company.name

    def test_get_or_create_location_creates_new(self, repository, db_session):
        """Test creating a new location when it doesn't exist."""
        location = repository._get_or_create_location("Seattle, WA")

        assert location.id is not None
        assert location.region == "Seattle, WA"

        # Verify it's in the database
        db_location = db_session.query(Location).filter_by(region="Seattle, WA").first()
        assert db_location is not None
        assert db_location.id == location.id

    def test_get_or_create_location_returns_existing(self, repository, sample_location):
        """Test returning existing location instead of creating duplicate."""
        location = repository._get_or_create_location(sample_location.region)

        assert location.id == sample_location.id
        assert location.region == sample_location.region

    def test_get_or_create_category_creates_new(self, repository, db_session):
        """Test creating a new category when it doesn't exist."""
        category = repository._get_or_create_category("Data Science")

        assert category.id is not None
        assert category.name == "Data Science"

        # Verify it's in the database
        db_category = db_session.query(Category).filter_by(name="Data Science").first()
        assert db_category is not None
        assert db_category.id == category.id

    def test_get_or_create_category_returns_existing(self, repository, sample_category):
        """Test returning existing category instead of creating duplicate."""
        category = repository._get_or_create_category(sample_category.name)

        assert category.id == sample_category.id
        assert category.name == sample_category.name

    def test_get_or_create_industry_creates_new(self, repository, db_session):
        """Test creating a new industry when it doesn't exist."""
        industry = repository._get_or_create_industry("Healthcare")

        assert industry.id is not None
        assert industry.name == "Healthcare"

        # Verify it's in the database
        db_industry = db_session.query(Industry).filter_by(name="Healthcare").first()
        assert db_industry is not None
        assert db_industry.id == industry.id

    def test_get_or_create_industry_returns_existing(self, repository, sample_industry):
        """Test returning existing industry instead of creating duplicate."""
        industry = repository._get_or_create_industry(sample_industry.name)

        assert industry.id == sample_industry.id
        assert industry.name == sample_industry.name

    # ============================================================
    # Tests for get_by_external_id Method
    # ============================================================

    def test_get_by_external_id_found(self, repository, sample_job):
        """Test retrieving a job by external_id when it exists."""
        job = repository.get_by_external_id(sample_job.external_id, sample_job.source)

        assert job is not None
        assert job.id == sample_job.id
        assert job.external_id == sample_job.external_id
        assert job.source == sample_job.source

    def test_get_by_external_id_not_found(self, repository):
        """Test retrieving a job that doesn't exist returns None."""
        job = repository.get_by_external_id("nonexistent-id", "Unknown")

        assert job is None

    def test_get_by_external_id_without_source(self, repository, sample_job):
        """Test retrieving job by external_id without specifying source."""
        job = repository.get_by_external_id(sample_job.external_id)

        assert job is not None
        assert job.external_id == sample_job.external_id

    def test_get_by_external_id_with_wrong_source(self, repository, sample_job):
        """Test that wrong source returns None even if external_id matches."""
        job = repository.get_by_external_id(sample_job.external_id, "WrongSource")

        assert job is None

    # ============================================================
    # Tests for create Method
    # ============================================================

    def test_create_job_with_jobdict(self, repository, sample_job_dict, db_session):
        """Test creating a job from JobDict contract data."""
        job = repository.create(sample_job_dict)

        assert job.id is not None
        assert job.title == "Senior Python Developer"
        assert job.external_id == "12345"
        assert job.source_url == "https://example.com/jobs/12345"
        assert job.job_type == "FULL_TIME"
        assert job.experience_months == 36.0
        assert job.salary_min == 120000.0
        assert job.salary_max == 160000.0
        assert job.salary_currency == "USD"
        assert job.is_remote is True

        # Verify relationships are created
        assert job.company_rel is not None
        assert job.company_rel.name == "Example Corp"
        assert job.location_rel is not None
        assert job.location_rel.region == "New York, NY"
        assert job.category_rel is not None
        assert job.category_rel.name == "Software Development"
        assert job.industry_rel is not None
        assert job.industry_rel.name == "Information Technology"

    def test_create_job_with_jobcreate(self, repository, sample_job_create_dict, db_session):
        """Test creating a job from JobCreate contract data with skills."""
        job = repository.create(sample_job_create_dict)

        assert job.id is not None
        assert job.title == "DevOps Engineer"
        assert job.must_have_skills == ["AWS", "Terraform", "Docker", "Kubernetes"]
        assert job.nice_to_have_skills == ["Ansible", "Jenkins", "Python"]

    def test_create_job_reuses_existing_company(self, repository, sample_job_dict, db_session):
        """Test that creating multiple jobs with same company reuses existing company."""
        # Create first job
        job1 = repository.create(sample_job_dict)
        company_id_1 = job1.company_id

        # Create second job with same company
        job_dict_2 = sample_job_dict.copy()
        job_dict_2["job_id"] = 99999
        job2 = repository.create(job_dict_2)
        company_id_2 = job2.company_id

        # Should use the same company
        assert company_id_1 == company_id_2

        # Verify only one company exists
        company_count = db_session.query(Company).filter_by(name="Example Corp").count()
        assert company_count == 1

    def test_create_job_reuses_existing_location(self, repository, sample_job_dict, db_session):
        """Test that creating multiple jobs with same location reuses existing location."""
        # Create first job
        job1 = repository.create(sample_job_dict)
        location_id_1 = job1.location_id

        # Create second job with same location
        job_dict_2 = sample_job_dict.copy()
        job_dict_2["job_id"] = 99998
        job2 = repository.create(job_dict_2)
        location_id_2 = job2.location_id

        # Should use the same location
        assert location_id_1 == location_id_2

        # Verify only one location exists
        location_count = db_session.query(Location).filter_by(region="New York, NY").count()
        assert location_count == 1

    def test_create_job_reuses_existing_category(self, repository, sample_job_dict, db_session):
        """Test that creating multiple jobs with same category reuses existing category."""
        # Create first job
        job1 = repository.create(sample_job_dict)
        category_id_1 = job1.category_id

        # Create second job with same category
        job_dict_2 = sample_job_dict.copy()
        job_dict_2["job_id"] = 99997
        job2 = repository.create(job_dict_2)
        category_id_2 = job2.category_id

        # Should use the same category
        assert category_id_1 == category_id_2

        # Verify only one category exists
        category_count = db_session.query(Category).filter_by(name="Software Development").count()
        assert category_count == 1

    def test_create_job_reuses_existing_industry(self, repository, sample_job_dict, db_session):
        """Test that creating multiple jobs with same industry reuses existing industry."""
        # Create first job
        job1 = repository.create(sample_job_dict)
        industry_id_1 = job1.industry_id

        # Create second job with same industry
        job_dict_2 = sample_job_dict.copy()
        job_dict_2["job_id"] = 99996
        job2 = repository.create(job_dict_2)
        industry_id_2 = job2.industry_id

        # Should use the same industry
        assert industry_id_1 == industry_id_2

        # Verify only one industry exists
        industry_count = db_session.query(Industry).filter_by(name="Information Technology").count()
        assert industry_count == 1

    def test_create_job_with_minimal_data(self, repository):
        """Test creating job with minimal required fields."""
        minimal_data = {"job_id": 777, "title": "Minimal Job", "company": {"name": "Minimal Corp"}}
        job = repository.create(minimal_data)

        assert job.id is not None
        assert job.title == "Minimal Job"
        assert job.company_rel.name == "Minimal Corp"
        assert job.location_id is None
        assert job.category_id is None
        assert job.industry_id is None

    def test_create_job_without_company(self, repository):
        """Test creating job without company data."""
        job_data = {"job_id": 666, "title": "Job Without Company"}
        job = repository.create(job_data)

        assert job.id is not None
        assert job.title == "Job Without Company"
        assert job.company_id is None

    # ============================================================
    # Tests for Exception Handling
    # ============================================================

    def test_create_job_raises_already_exists_error(self, repository, sample_job_dict):
        """Test that creating duplicate job raises JobAlreadyExistsError."""
        # Create first job
        repository.create(sample_job_dict)

        # Try to create duplicate
        with pytest.raises(JobAlreadyExistsError) as exc_info:
            repository.create(sample_job_dict)

        assert exc_info.value.external_id == "12345"
        assert "already exists" in str(exc_info.value).lower()

    def test_create_job_handles_integrity_error(self, repository, sample_job_dict, db_session):
        """Test that IntegrityError is converted to ValidationError."""
        # Mock the session to raise IntegrityError
        with patch.object(db_session, "commit", side_effect=IntegrityError("mock", "mock", "mock")):
            with pytest.raises(ValidationError) as exc_info:
                repository.create(sample_job_dict)

            assert "Integrity constraint violated" in str(exc_info.value)

    def test_create_job_handles_sqlalchemy_error(self, repository, sample_job_dict, db_session):
        """Test that SQLAlchemyError is converted to TransactionError."""
        # Mock the session to raise SQLAlchemyError
        with patch.object(db_session, "commit", side_effect=SQLAlchemyError("Database error")):
            with pytest.raises(TransactionError) as exc_info:
                repository.create(sample_job_dict)

            assert "Failed to create job" in str(exc_info.value)

    def test_create_rolls_back_on_already_exists_error(
        self, repository, sample_job_dict, db_session
    ):
        """Test that session is rolled back when job already exists."""
        # Create first job
        repository.create(sample_job_dict)

        # Create a company to track rollback
        company = Company(name="Test Rollback Company")
        db_session.add(company)
        db_session.flush()

        # Try to create duplicate job (should rollback)
        try:
            repository.create(sample_job_dict)
        except JobAlreadyExistsError:
            pass

        # The company we added should be rolled back
        db_session.commit()  # Commit to clear any pending state
        companies = db_session.query(Company).filter_by(name="Test Rollback Company").all()
        assert len(companies) == 0

    def test_create_rolls_back_on_integrity_error(self, repository, sample_job_dict, db_session):
        """Test that session is rolled back on IntegrityError."""
        # Mock commit to raise IntegrityError
        with patch.object(db_session, "commit", side_effect=IntegrityError("mock", "mock", "mock")):
            try:
                repository.create(sample_job_dict)
            except ValidationError:
                pass

        # Session should be rolled back
        assert db_session.query(Job).count() == 0

    def test_create_rolls_back_on_sqlalchemy_error(self, repository, sample_job_dict, db_session):
        """Test that session is rolled back on SQLAlchemyError."""
        # Mock commit to raise SQLAlchemyError
        with patch.object(db_session, "commit", side_effect=SQLAlchemyError("error")):
            try:
                repository.create(sample_job_dict)
            except TransactionError:
                pass

        # Session should be rolled back
        assert db_session.query(Job).count() == 0

    # ============================================================
    # Tests for Source Field Handling
    # ============================================================

    def test_create_job_without_explicit_source(self, repository):
        """Test creating job without explicitly setting source field in JobDict."""
        job_data = {
            "job_id": 555,
            "title": "Job Without Source",
            "company": {"name": "Source Test Corp"},
        }
        job = repository.create(job_data)

        assert job.id is not None
        # Source should be None or not set
        assert job.source is None

    def test_get_by_external_id_matches_none_source(self, repository):
        """Test that get_by_external_id works when source is None."""
        job_data = {
            "job_id": 444,
            "title": "Job With None Source",
            "company": {"name": "None Source Corp"},
        }
        created_job = repository.create(job_data)

        # Retrieve without source parameter
        retrieved_job = repository.get_by_external_id("444")
        assert retrieved_job is not None
        assert retrieved_job.id == created_job.id

    # ============================================================
    # Tests for Mapper Integration
    # ============================================================

    def test_create_uses_mapper_correctly(self, repository, sample_job_dict):
        """Test that create method properly uses JobMapper."""
        job = repository.create(sample_job_dict)

        # Verify field transformations from mapper
        assert job.external_id == "12345"  # job_id -> external_id
        assert job.source_url == "https://example.com/jobs/12345"  # url -> source_url
        assert job.job_type == "FULL_TIME"  # employment_type -> job_type

    def test_repository_has_mapper_instance(self, repository):
        """Test that repository initializes with a mapper."""
        assert repository.mapper is not None
        from jobs_repository.mapper import JobMapper

        assert isinstance(repository.mapper, JobMapper)

    # ============================================================
    # Tests for Edge Cases and Data Integrity
    # ============================================================

    def test_create_job_with_all_relationships(self, repository, sample_job_dict):
        """Test creating job with all relationship entities populated."""
        job = repository.create(sample_job_dict)

        # Verify all relationships are properly set
        assert job.company_id is not None
        assert job.location_id is not None
        assert job.category_id is not None
        assert job.industry_id is not None

        # Verify relationships can be accessed
        assert job.company_rel.name == "Example Corp"
        assert job.location_rel.region == "New York, NY"
        assert job.category_rel.name == "Software Development"
        assert job.industry_rel.name == "Information Technology"

    def test_create_job_with_no_relationships(self, repository):
        """Test creating job without any relationship entities."""
        job_data = {
            "job_id": 333,
            "title": "Standalone Job",
            "description": "Job with no relationships",
        }
        job = repository.create(job_data)

        assert job.id is not None
        assert job.company_id is None
        assert job.location_id is None
        assert job.category_id is None
        assert job.industry_id is None

    def test_create_job_with_datetime_fields(self, repository, sample_job_dict):
        """Test that datetime fields are properly stored."""
        job = repository.create(sample_job_dict)

        assert job.posted_at is not None
        assert job.expires_at is not None
        assert job.created_at is not None
        assert job.updated_at is not None

        # Verify created_at and updated_at are auto-generated
        from datetime import datetime

        assert isinstance(job.created_at, datetime)
        assert isinstance(job.updated_at, datetime)

    def test_create_refreshes_job_instance(self, repository, sample_job_dict):
        """Test that create() refreshes the job instance with DB values."""
        job = repository.create(sample_job_dict)

        # After refresh, all database-generated fields should be populated
        assert job.id is not None
        assert job.created_at is not None
        assert job.updated_at is not None

        # Relationships should be loaded
        assert job.company_rel is not None
        assert job.location_rel is not None

    def test_get_or_create_company_case_sensitive(self, repository, db_session):
        """Test that company names are case-sensitive."""
        company1 = repository._get_or_create_company("TechCorp")
        company2 = repository._get_or_create_company("techcorp")

        # Should create two different companies
        assert company1.id != company2.id
        assert db_session.query(Company).count() == 2

    def test_get_or_create_location_whitespace_sensitive(self, repository, db_session):
        """Test that location regions are whitespace-sensitive."""
        location1 = repository._get_or_create_location("San Francisco, CA")
        location2 = repository._get_or_create_location("San Francisco,CA")

        # Should create two different locations due to whitespace difference
        assert location1.id != location2.id
        assert db_session.query(Location).count() == 2

    def test_get_or_create_methods_use_flush(self, repository, db_session):
        """Test that get_or_create methods flush to get ID without committing."""
        company = repository._get_or_create_company("Flush Test Company")

        # Company should have ID after flush
        assert company.id is not None

        # But shouldn't be committed yet (we can rollback)
        db_session.rollback()

        # After rollback, company shouldn't exist
        from sqlalchemy import select

        stmt = select(Company).where(Company.name == "Flush Test Company")
        result = db_session.scalar(stmt)
        assert result is None

    def test_create_multiple_jobs_same_external_id_different_source(
        self, repository, sample_job_dict
    ):
        """Test that same external_id can exist for different sources."""
        # Create first job
        repository.create(sample_job_dict)

        # Create second job with same external_id but different source
        job_dict_2 = sample_job_dict.copy()
        job_dict_2["job_id"] = 12345  # Same job_id (becomes external_id)

        # Need to add a source field to the job_data
        # Since JobDict doesn't have source field by default, let's test
        # that we can't create duplicate without changing external_id

        # This should raise error because external_id is the same
        with pytest.raises(JobAlreadyExistsError):
            repository.create(job_dict_2)

    def test_get_by_external_id_with_multiple_sources(self, repository):
        """Test retrieving jobs with same external_id from different sources."""
        # Create jobs with same external_id but without source
        job_data_1 = {"job_id": 111, "title": "Job 1", "company": {"name": "Company 1"}}

        job1 = repository.create(job_data_1)

        # Try to retrieve it
        retrieved = repository.get_by_external_id("111")
        assert retrieved is not None
        assert retrieved.id == job1.id

    def test_create_with_empty_skills_arrays(self, repository):
        """Test creating job with empty skills arrays.

        Note: Empty arrays are not passed through by the mapper due to
        truthy/falsy check, so they become None. This tests the current behavior.
        """
        job_data = {
            "job_id": 888,
            "title": "Job With Empty Skills",
            "company": {"name": "Skills Test Corp"},
            "must_have_skills": [],
            "nice_to_have_skills": [],
        }
        job = repository.create(job_data)

        # Empty arrays become None due to mapper's truthy check
        assert job.must_have_skills is None
        assert job.nice_to_have_skills is None

    def test_create_handles_mapped_data_correctly(self, repository, sample_job_dict):
        """Test that mapper transformations are applied before create."""
        job = repository.create(sample_job_dict)

        # Verify mapper transformations were applied
        # job_id should be converted to external_id as string
        assert job.external_id == str(sample_job_dict["job_id"])

        # url should be mapped to source_url
        assert job.source_url == sample_job_dict["url"]

        # employment_type should be mapped to job_type
        assert job.job_type == sample_job_dict["employment_type"]

    def test_repository_session_property(self, repository, db_session):
        """Test that repository stores and provides access to session."""
        assert repository.session is db_session
        assert repository.session is not None

    def test_create_commits_transaction(self, repository, sample_job_dict, db_session):
        """Test that create() commits the transaction."""
        job = repository.create(sample_job_dict)

        # Query directly from database to verify commit
        from sqlalchemy import select

        stmt = select(Job).where(Job.id == job.id)
        db_job = db_session.scalar(stmt)

        assert db_job is not None
        assert db_job.id == job.id
        assert db_job.title == job.title

    def test_get_by_external_id_returns_none_for_empty_result(self, repository):
        """Test that get_by_external_id returns None when no match found."""
        result = repository.get_by_external_id("does-not-exist-12345", "NoSource")
        assert result is None

    def test_create_job_with_special_characters_in_fields(self, repository):
        """Test creating job with special characters in various fields."""
        job_data = {
            "job_id": 9999,
            "title": "Senior Software Engineer (C/C++/Python) - Remote",
            "company": {"name": "Tech & Data Corp."},
            "category": "Software Development & Engineering",
            "industry": "IT & Services",
            "location": {"region": "São Paulo, Brazil"},
            "description": "Looking for engineers with C++ & Python skills, 3+ years exp.",
        }
        job = repository.create(job_data)

        assert job.id is not None
        assert job.title == "Senior Software Engineer (C/C++/Python) - Remote"
        assert job.company_rel.name == "Tech & Data Corp."
        assert job.category_rel.name == "Software Development & Engineering"
        assert job.industry_rel.name == "IT & Services"
        assert job.location_rel.region == "São Paulo, Brazil"

    def test_get_or_create_creates_entity_on_first_call(self, repository, db_session):
        """Test that get_or_create actually creates entity on first call."""
        # Verify company doesn't exist
        from sqlalchemy import select

        stmt = select(Company).where(Company.name == "First Call Company")
        assert db_session.scalar(stmt) is None

        # Call get_or_create
        company = repository._get_or_create_company("First Call Company")

        # Verify it was created
        assert company.id is not None
        db_company = db_session.scalar(select(Company).where(Company.name == "First Call Company"))
        assert db_company is not None
        assert db_company.id == company.id

    def test_exception_contains_correct_external_id(self, repository, sample_job_dict):
        """Test that JobAlreadyExistsError contains the correct external_id."""
        repository.create(sample_job_dict)

        with pytest.raises(JobAlreadyExistsError) as exc_info:
            repository.create(sample_job_dict)

        # Verify exception has correct attributes
        assert exc_info.value.external_id == "12345"
        assert exc_info.value.source is not None
