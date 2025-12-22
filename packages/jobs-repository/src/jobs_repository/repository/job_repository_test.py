"""Tests for JobRepository class."""

from unittest.mock import patch, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from jobs_repository.repository import JobRepository
from jobs_repository.models import Job, Company, Location, Category, Industry
from job_agent_platform_contracts.job_repository.exceptions import (
    JobAlreadyExistsError,
    ValidationError,
)
from db_core import TransactionError


class TestJobRepository:
    """Test suite for JobRepository class."""

    @pytest.fixture
    def repository(self, reference_data_service, job_mapper, db_session):
        """Create a JobRepository instance."""
        return JobRepository(reference_data_service, job_mapper, db_session)

    def test_get_by_external_id_returns_job_when_exists(self, repository, sample_job):
        """Test retrieving a job by external_id when it exists."""
        job = repository.get_by_external_id(sample_job.external_id, sample_job.source)

        assert job is not None
        assert job.id == sample_job.id
        assert job.external_id == sample_job.external_id
        assert job.source == sample_job.source

    def test_get_by_external_id_returns_none_when_not_exists(self, repository):
        """Test retrieving a job that doesn't exist returns None."""
        job = repository.get_by_external_id("nonexistent-id", "Unknown")

        assert job is None

    def test_get_by_external_id_returns_job_when_source_omitted(self, repository, sample_job):
        """Test retrieving job by external_id without specifying source."""
        job = repository.get_by_external_id(sample_job.external_id)

        assert job is not None
        assert job.external_id == sample_job.external_id

    def test_get_by_external_id_returns_none_when_source_mismatch(self, repository, sample_job):
        """Test that wrong source returns None even if external_id matches."""
        job = repository.get_by_external_id(sample_job.external_id, "WrongSource")

        assert job is None

    def test_create_stores_all_jobdict_fields_correctly(
        self, repository, sample_job_dict, db_session
    ):
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

        assert job.company_rel is not None
        assert job.company_rel.name == "Example Corp"
        assert job.location_rel is not None
        assert job.location_rel.region == "New York, NY"
        assert job.category_rel is not None
        assert job.category_rel.name == "Software Development"
        assert job.industry_rel is not None
        assert job.industry_rel.name == "Information Technology"

    def test_create_stores_skills_from_jobcreate(
        self, repository, sample_job_create_dict, db_session
    ):
        """Test creating a job from JobCreate contract data with skills."""
        job = repository.create(sample_job_create_dict)

        assert job.id is not None
        assert job.title == "DevOps Engineer"
        assert job.must_have_skills == ["AWS", "Terraform", "Docker", "Kubernetes"]
        assert job.nice_to_have_skills == ["Ansible", "Jenkins", "Python"]

    def test_create_job_reuses_existing_company(self, repository, sample_job_dict, db_session):
        """Test that creating multiple jobs with same company reuses existing company."""

        job1 = repository.create(sample_job_dict)
        company_id_1 = job1.company_id

        job_dict_2 = sample_job_dict.copy()
        job_dict_2["job_id"] = 99999
        job_dict_2["url"] = "https://example.com/jobs/99999"
        job2 = repository.create(job_dict_2)
        company_id_2 = job2.company_id

        assert company_id_1 == company_id_2

        company_count = db_session.query(Company).filter_by(name="Example Corp").count()
        assert company_count == 1

    def test_create_job_reuses_existing_location(self, repository, sample_job_dict, db_session):
        """Test that creating multiple jobs with same location reuses existing location."""

        job1 = repository.create(sample_job_dict)
        location_id_1 = job1.location_id

        job_dict_2 = sample_job_dict.copy()
        job_dict_2["job_id"] = 99998
        job_dict_2["url"] = "https://example.com/jobs/99998"
        job2 = repository.create(job_dict_2)
        location_id_2 = job2.location_id

        assert location_id_1 == location_id_2

        location_count = db_session.query(Location).filter_by(region="New York, NY").count()
        assert location_count == 1

    def test_create_job_reuses_existing_category(self, repository, sample_job_dict, db_session):
        """Test that creating multiple jobs with same category reuses existing category."""

        job1 = repository.create(sample_job_dict)
        category_id_1 = job1.category_id

        job_dict_2 = sample_job_dict.copy()
        job_dict_2["job_id"] = 99997
        job_dict_2["url"] = "https://example.com/jobs/99997"
        job2 = repository.create(job_dict_2)
        category_id_2 = job2.category_id

        assert category_id_1 == category_id_2

        category_count = db_session.query(Category).filter_by(name="Software Development").count()
        assert category_count == 1

    def test_create_job_reuses_existing_industry(self, repository, sample_job_dict, db_session):
        """Test that creating multiple jobs with same industry reuses existing industry."""

        job1 = repository.create(sample_job_dict)
        industry_id_1 = job1.industry_id

        job_dict_2 = sample_job_dict.copy()
        job_dict_2["job_id"] = 99996
        job_dict_2["url"] = "https://example.com/jobs/99996"
        job2 = repository.create(job_dict_2)
        industry_id_2 = job2.industry_id

        assert industry_id_1 == industry_id_2

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

    def test_create_job_raises_already_exists_error(self, repository, sample_job_dict):
        """Test that creating duplicate job raises JobAlreadyExistsError."""

        repository.create(sample_job_dict)

        with pytest.raises(JobAlreadyExistsError) as exc_info:
            repository.create(sample_job_dict)

        assert exc_info.value.external_id == "12345"
        assert "already exists" in str(exc_info.value).lower()

    def test_create_job_handles_integrity_error(self, repository, sample_job_dict, db_session):
        """Test that IntegrityError is converted to ValidationError."""

        with patch.object(db_session, "commit", side_effect=IntegrityError("mock", "mock", "mock")):
            with pytest.raises(ValidationError) as exc_info:
                repository.create(sample_job_dict)

            assert "Integrity constraint violated" in str(exc_info.value)

    def test_create_job_handles_sqlalchemy_error(self, repository, sample_job_dict, db_session):
        """Test that SQLAlchemyError is converted to TransactionError."""

        with patch.object(db_session, "commit", side_effect=SQLAlchemyError("Database error")):
            with pytest.raises(TransactionError) as exc_info:
                repository.create(sample_job_dict)

            assert "Failed to create job" in str(exc_info.value)

    def test_create_rolls_back_on_already_exists_error(
        self, repository, sample_job_dict, db_session
    ):
        """Test that session is rolled back when job already exists."""

        repository.create(sample_job_dict)

        company = Company(name="Test Rollback Company")
        db_session.add(company)
        db_session.flush()

        try:
            repository.create(sample_job_dict)
        except JobAlreadyExistsError:
            pass

        db_session.commit()
        companies = db_session.query(Company).filter_by(name="Test Rollback Company").all()
        assert len(companies) == 0

    def test_create_rolls_back_on_integrity_error(self, repository, sample_job_dict, db_session):
        """Test that session is rolled back on IntegrityError."""

        with patch.object(db_session, "commit", side_effect=IntegrityError("mock", "mock", "mock")):
            try:
                repository.create(sample_job_dict)
            except ValidationError:
                pass

        assert db_session.query(Job).count() == 0

    def test_create_rolls_back_on_sqlalchemy_error(self, repository, sample_job_dict, db_session):
        """Test that session is rolled back on SQLAlchemyError."""

        with patch.object(db_session, "commit", side_effect=SQLAlchemyError("error")):
            try:
                repository.create(sample_job_dict)
            except TransactionError:
                pass

        assert db_session.query(Job).count() == 0

    def test_create_job_without_explicit_source(self, repository):
        """Test creating job without explicitly setting source field in JobDict."""
        job_data = {
            "job_id": 555,
            "title": "Job Without Source",
            "company": {"name": "Source Test Corp"},
        }
        job = repository.create(job_data)

        assert job.id is not None

        assert job.source is None

    def test_get_by_external_id_matches_none_source(self, repository):
        """Test that get_by_external_id works when source is None."""
        job_data = {
            "job_id": 444,
            "title": "Job With None Source",
            "company": {"name": "None Source Corp"},
        }
        created_job = repository.create(job_data)

        retrieved_job = repository.get_by_external_id("444")
        assert retrieved_job is not None
        assert retrieved_job.id == created_job.id

    def test_create_uses_mapper_correctly(self, repository, sample_job_dict):
        """Test that create method properly uses JobMapper."""
        job = repository.create(sample_job_dict)

        assert job.external_id == "12345"
        assert job.source_url == "https://example.com/jobs/12345"
        assert job.job_type == "FULL_TIME"

    def test_create_job_with_all_relationships(self, repository, sample_job_dict):
        """Test creating job with all relationship entities populated."""
        job = repository.create(sample_job_dict)

        assert job.company_id is not None
        assert job.location_id is not None
        assert job.category_id is not None
        assert job.industry_id is not None

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

        from datetime import datetime

        assert isinstance(job.created_at, datetime)
        assert isinstance(job.updated_at, datetime)

    def test_create_refreshes_job_instance(self, repository, sample_job_dict):
        """Test that create() refreshes the job instance with DB values."""
        job = repository.create(sample_job_dict)

        assert job.id is not None
        assert job.created_at is not None
        assert job.updated_at is not None

        assert job.company_rel is not None
        assert job.location_rel is not None

    def test_create_multiple_jobs_same_external_id_different_source(
        self, repository, sample_job_dict
    ):
        """Test that same external_id can exist for different sources."""

        repository.create(sample_job_dict)

        job_dict_2 = sample_job_dict.copy()
        job_dict_2["job_id"] = 12345

        with pytest.raises(JobAlreadyExistsError):
            repository.create(job_dict_2)

    def test_get_by_external_id_with_multiple_sources(self, repository):
        """Test retrieving jobs with same external_id from different sources."""

        job_data_1 = {"job_id": 111, "title": "Job 1", "company": {"name": "Company 1"}}

        job1 = repository.create(job_data_1)

        retrieved = repository.get_by_external_id("111")
        assert retrieved is not None
        assert retrieved.id == job1.id

    def test_create_preserves_empty_skills_arrays(self, repository):
        """Test creating job with empty skills arrays.

        Empty skill lists explicitly indicate "no skills found" which is
        semantically different from "skills not extracted" (None/missing).
        Empty lists SHOULD be preserved to maintain this distinction.
        """
        job_data = {
            "job_id": 888,
            "title": "Job With Empty Skills",
            "company": {"name": "Skills Test Corp"},
            "must_have_skills": [],
            "nice_to_have_skills": [],
        }
        job = repository.create(job_data)

        assert job.must_have_skills == []
        assert job.nice_to_have_skills == []

    def test_create_handles_mapped_data_correctly(self, repository, sample_job_dict):
        """Test that mapper transformations are applied before create."""
        job = repository.create(sample_job_dict)

        assert job.external_id == str(sample_job_dict["job_id"])

        assert job.source_url == sample_job_dict["url"]

        assert job.job_type == sample_job_dict["employment_type"]

    def test_repository_commits_with_provided_session(
        self, repository, sample_job_dict, db_session
    ):
        """Test that repository uses provided session for committing changes."""
        with patch.object(db_session, "commit") as mock_commit:
            repository.create(sample_job_dict)

        mock_commit.assert_called_once()

    def test_create_with_internal_session_factory(
        self, reference_data_service, job_mapper, in_memory_engine, sample_job_dict
    ):
        """Test that repository manages its own sessions when factory provided."""
        factory = sessionmaker(bind=in_memory_engine)
        repository = JobRepository(reference_data_service, job_mapper, session_factory=factory)

        job = repository.create(sample_job_dict)

        assert job.id is not None

    def test_get_job_repository_uses_container(self):
        """Test that container factory produces repository instances."""
        from jobs_repository.container import container, get_job_repository

        mock_factory = MagicMock(return_value="repository")

        with container.job_repository.override(mock_factory):
            repo_instance = get_job_repository()

        mock_factory.assert_called_once()
        assert repo_instance == "repository"

    def test_create_commits_transaction(self, repository, sample_job_dict, db_session):
        """Test that create() commits the transaction."""
        job = repository.create(sample_job_dict)

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

    def test_exception_contains_correct_external_id(self, repository, sample_job_dict):
        """Test that JobAlreadyExistsError contains the correct external_id."""
        repository.create(sample_job_dict)

        with pytest.raises(JobAlreadyExistsError) as exc_info:
            repository.create(sample_job_dict)

        assert exc_info.value.external_id == "12345"
        assert exc_info.value.source == "unknown"


class TestJobRepositoryConstructor:
    """Tests for JobRepository constructor validation."""

    def test_raises_error_when_both_session_and_factory_provided(
        self, reference_data_service, job_mapper, db_session
    ):
        """Test that providing both session and session_factory raises ValueError."""

        def factory():
            return db_session

        with pytest.raises(ValueError) as exc_info:
            JobRepository(
                reference_data_service,
                job_mapper,
                session=db_session,
                session_factory=factory,
            )

        assert "either session or session_factory" in str(exc_info.value).lower()

    def test_raises_error_when_session_factory_not_callable(
        self, reference_data_service, job_mapper
    ):
        """Test that non-callable session_factory raises TypeError."""
        with pytest.raises(TypeError) as exc_info:
            JobRepository(
                reference_data_service,
                job_mapper,
                session_factory="not_callable",
            )

        assert "callable" in str(exc_info.value).lower()

    def test_accepts_session_only(self, reference_data_service, job_mapper, db_session):
        """Test that repository can be created with session only."""
        repo = JobRepository(reference_data_service, job_mapper, session=db_session)

        assert repo is not None
        assert repo._close_session is False

    def test_accepts_session_factory_only(
        self, reference_data_service, job_mapper, in_memory_engine
    ):
        """Test that repository can be created with session_factory only."""
        factory = sessionmaker(bind=in_memory_engine)
        repo = JobRepository(reference_data_service, job_mapper, session_factory=factory)

        assert repo is not None
        assert repo._close_session is True


class TestJobRepositoryHasActiveJobWithTitleAndCompany:
    """Tests for has_active_job_with_title_and_company method."""

    @pytest.fixture
    def repository(self, reference_data_service, job_mapper, db_session):
        """Create a JobRepository instance."""
        return JobRepository(reference_data_service, job_mapper, db_session)

    def test_has_active_job_returns_true_when_active_job_exists(
        self, repository, reference_data_service, db_session
    ):
        """Test returns True when matching active job exists."""
        from datetime import datetime, timedelta, UTC

        company = reference_data_service.get_or_create_company(db_session, "Active Test Corp")
        future_date = datetime.now(UTC) + timedelta(days=30)
        # Handle timezone-naive column
        if not getattr(Job.__table__.c.expires_at.type, "timezone", False):
            future_date = future_date.replace(tzinfo=None)

        job = Job(
            title="Active Test Job",
            company_id=company.id,
            external_id="active-test-1",
            expires_at=future_date,
        )
        db_session.add(job)
        db_session.commit()

        result = repository.has_active_job_with_title_and_company(
            "Active Test Job", "Active Test Corp"
        )

        assert result is True

    def test_has_active_job_returns_false_when_no_matching_job(self, repository, sample_job):
        """Test returns False when no job matches title and company."""
        result = repository.has_active_job_with_title_and_company(
            "Nonexistent Title", "Nonexistent Company"
        )

        assert result is False

    def test_has_active_job_returns_false_when_title_mismatch(self, repository, sample_job):
        """Test returns False when title matches but company doesn't."""
        result = repository.has_active_job_with_title_and_company(sample_job.title, "Wrong Company")

        assert result is False

    def test_has_active_job_returns_false_when_company_mismatch(self, repository, sample_job):
        """Test returns False when company matches but title doesn't."""
        result = repository.has_active_job_with_title_and_company(
            "Wrong Title", sample_job.company_rel.name
        )

        assert result is False

    def test_has_active_job_returns_true_when_job_has_no_expiry(
        self, repository, reference_data_service, db_session
    ):
        """Test returns True when matching job has no expiry date."""
        company = reference_data_service.get_or_create_company(db_session, "No Expiry Corp")
        job = Job(
            title="No Expiry Job",
            company_id=company.id,
            external_id="no-expiry-1",
            expires_at=None,
        )
        db_session.add(job)
        db_session.commit()

        result = repository.has_active_job_with_title_and_company("No Expiry Job", "No Expiry Corp")

        assert result is True

    def test_has_active_job_returns_false_when_job_is_expired(
        self, repository, reference_data_service, db_session
    ):
        """Test returns False when matching job is expired."""
        from datetime import datetime, timedelta, UTC

        company = reference_data_service.get_or_create_company(db_session, "Expired Corp")
        expired_date = datetime.now(UTC) - timedelta(days=1)
        # Handle timezone-naive column
        if not getattr(Job.__table__.c.expires_at.type, "timezone", False):
            expired_date = expired_date.replace(tzinfo=None)

        job = Job(
            title="Expired Job",
            company_id=company.id,
            external_id="expired-1",
            expires_at=expired_date,
        )
        db_session.add(job)
        db_session.commit()

        result = repository.has_active_job_with_title_and_company("Expired Job", "Expired Corp")

        assert result is False

    def test_has_active_job_returns_true_when_job_expires_in_future(
        self, repository, reference_data_service, db_session
    ):
        """Test returns True when matching job expires in the future."""
        from datetime import datetime, timedelta, UTC

        company = reference_data_service.get_or_create_company(db_session, "Future Corp")
        future_date = datetime.now(UTC) + timedelta(days=30)
        # Handle timezone-naive column
        if not getattr(Job.__table__.c.expires_at.type, "timezone", False):
            future_date = future_date.replace(tzinfo=None)

        job = Job(
            title="Future Job",
            company_id=company.id,
            external_id="future-1",
            expires_at=future_date,
        )
        db_session.add(job)
        db_session.commit()

        result = repository.has_active_job_with_title_and_company("Future Job", "Future Corp")

        assert result is True


class TestJobRepositoryGetExistingUrlsBySource:
    """Tests for get_existing_urls_by_source method."""

    @pytest.fixture
    def repository(self, reference_data_service, job_mapper, db_session):
        """Create a JobRepository instance."""
        return JobRepository(reference_data_service, job_mapper, db_session)

    def test_get_existing_urls_returns_empty_list_when_no_jobs(self, repository):
        """Test returns empty list when no jobs exist for source."""
        result = repository.get_existing_urls_by_source("nonexistent_source")

        assert result == []

    def test_get_existing_urls_returns_urls_for_matching_source(self, repository, db_session):
        """Test returns URLs for jobs with matching source."""
        from datetime import datetime, UTC

        posted_at = datetime.now(UTC)
        if not getattr(Job.__table__.c.posted_at.type, "timezone", False):
            posted_at = posted_at.replace(tzinfo=None)

        job1 = Job(
            title="Job 1",
            external_id="url-test-1",
            source="djinni",
            source_url="https://djinni.co/jobs/1",
            posted_at=posted_at,
        )
        job2 = Job(
            title="Job 2",
            external_id="url-test-2",
            source="djinni",
            source_url="https://djinni.co/jobs/2",
            posted_at=posted_at,
        )
        db_session.add_all([job1, job2])
        db_session.commit()

        result = repository.get_existing_urls_by_source("djinni")

        assert len(result) == 2
        assert "https://djinni.co/jobs/1" in result
        assert "https://djinni.co/jobs/2" in result

    def test_get_existing_urls_excludes_jobs_from_other_sources(self, repository, db_session):
        """Test excludes URLs from jobs with different source."""
        from datetime import datetime, UTC

        posted_at = datetime.now(UTC)
        if not getattr(Job.__table__.c.posted_at.type, "timezone", False):
            posted_at = posted_at.replace(tzinfo=None)

        job1 = Job(
            title="Djinni Job",
            external_id="source-test-1",
            source="djinni",
            source_url="https://djinni.co/jobs/1",
            posted_at=posted_at,
        )
        job2 = Job(
            title="LinkedIn Job",
            external_id="source-test-2",
            source="linkedin",
            source_url="https://linkedin.com/jobs/2",
            posted_at=posted_at,
        )
        db_session.add_all([job1, job2])
        db_session.commit()

        result = repository.get_existing_urls_by_source("djinni")

        assert len(result) == 1
        assert "https://djinni.co/jobs/1" in result
        assert "https://linkedin.com/jobs/2" not in result

    def test_get_existing_urls_excludes_jobs_with_null_source_url(self, repository, db_session):
        """Test excludes jobs where source_url is None."""
        from datetime import datetime, UTC

        posted_at = datetime.now(UTC)
        if not getattr(Job.__table__.c.posted_at.type, "timezone", False):
            posted_at = posted_at.replace(tzinfo=None)

        job1 = Job(
            title="Job With URL",
            external_id="null-url-test-1",
            source="djinni",
            source_url="https://djinni.co/jobs/1",
            posted_at=posted_at,
        )
        job2 = Job(
            title="Job Without URL",
            external_id="null-url-test-2",
            source="djinni",
            source_url=None,
            posted_at=posted_at,
        )
        db_session.add_all([job1, job2])
        db_session.commit()

        result = repository.get_existing_urls_by_source("djinni")

        assert len(result) == 1
        assert "https://djinni.co/jobs/1" in result

    def test_get_existing_urls_filters_by_days_parameter(self, repository, db_session):
        """Test filters jobs by posted_at within days parameter."""
        from datetime import datetime, timedelta, UTC

        now = datetime.now(UTC)
        recent = now - timedelta(days=5)
        old = now - timedelta(days=30)

        if not getattr(Job.__table__.c.posted_at.type, "timezone", False):
            recent = recent.replace(tzinfo=None)
            old = old.replace(tzinfo=None)

        job_recent = Job(
            title="Recent Job",
            external_id="days-test-1",
            source="djinni",
            source_url="https://djinni.co/jobs/recent",
            posted_at=recent,
        )
        job_old = Job(
            title="Old Job",
            external_id="days-test-2",
            source="djinni",
            source_url="https://djinni.co/jobs/old",
            posted_at=old,
        )
        db_session.add_all([job_recent, job_old])
        db_session.commit()

        result = repository.get_existing_urls_by_source("djinni", days=7)

        assert len(result) == 1
        assert "https://djinni.co/jobs/recent" in result
        assert "https://djinni.co/jobs/old" not in result

    def test_get_existing_urls_returns_all_when_days_is_none(self, repository, db_session):
        """Test returns all URLs when days parameter is None."""
        from datetime import datetime, timedelta, UTC

        now = datetime.now(UTC)
        recent = now - timedelta(days=5)
        old = now - timedelta(days=365)

        if not getattr(Job.__table__.c.posted_at.type, "timezone", False):
            recent = recent.replace(tzinfo=None)
            old = old.replace(tzinfo=None)

        job_recent = Job(
            title="Recent Job",
            external_id="all-urls-1",
            source="djinni",
            source_url="https://djinni.co/jobs/recent",
            posted_at=recent,
        )
        job_old = Job(
            title="Old Job",
            external_id="all-urls-2",
            source="djinni",
            source_url="https://djinni.co/jobs/old",
            posted_at=old,
        )
        db_session.add_all([job_recent, job_old])
        db_session.commit()

        result = repository.get_existing_urls_by_source("djinni", days=None)

        assert len(result) == 2
        assert "https://djinni.co/jobs/recent" in result
        assert "https://djinni.co/jobs/old" in result

    def test_get_existing_urls_returns_list_type(self, repository):
        """Test that return type is always a list."""
        result = repository.get_existing_urls_by_source("any_source")

        assert isinstance(result, list)


class TestJobRepositoryDuplicateDetectionBySourceUrl:
    """Tests for duplicate detection via source_url."""

    @pytest.fixture
    def repository(self, reference_data_service, job_mapper, db_session):
        """Create a JobRepository instance."""
        return JobRepository(reference_data_service, job_mapper, db_session)

    def test_detects_duplicate_by_source_url(self, repository):
        """Test that duplicate is detected by source_url even with different external_id."""
        job_data_1 = {
            "job_id": 1001,
            "title": "First Job",
            "url": "https://example.com/jobs/same-url",
            "company": {"name": "Test Corp"},
        }
        repository.create(job_data_1)

        job_data_2 = {
            "job_id": 1002,
            "title": "Second Job",
            "url": "https://example.com/jobs/same-url",
            "company": {"name": "Test Corp"},
        }

        with pytest.raises(JobAlreadyExistsError):
            repository.create(job_data_2)


class TestJobRepositoryIsRelevant:
    """Tests for JobRepository is_relevant field handling."""

    @pytest.fixture
    def repository(self, reference_data_service, job_mapper, db_session):
        """Create a JobRepository instance."""
        return JobRepository(reference_data_service, job_mapper, db_session)

    def test_create_job_with_is_relevant_true(self, repository):
        """Test creating a job with is_relevant=True."""
        job_data = {
            "job_id": 2001,
            "title": "Relevant Job",
            "company": {"name": "Relevant Corp"},
            "is_relevant": True,
        }

        job = repository.create(job_data)

        assert job.id is not None
        assert job.is_relevant is True

    def test_create_job_with_is_relevant_false(self, repository):
        """Test creating a job with is_relevant=False."""
        job_data = {
            "job_id": 2002,
            "title": "Irrelevant Job",
            "company": {"name": "Irrelevant Corp"},
            "is_relevant": False,
        }

        job = repository.create(job_data)

        assert job.id is not None
        assert job.is_relevant is False

    def test_create_job_defaults_is_relevant_to_true(self, repository):
        """Test that is_relevant defaults to True when not specified in JobCreate."""
        job_data = {
            "job_id": 2003,
            "title": "Default Relevance Job",
            "company": {"name": "Default Corp"},
        }

        job = repository.create(job_data)

        assert job.id is not None
        assert job.is_relevant is True

    def test_create_job_is_relevant_persists_correctly(self, repository, db_session):
        """Test that is_relevant value is correctly persisted to database."""
        job_data = {
            "job_id": 2004,
            "title": "Persisted Irrelevant Job",
            "company": {"name": "Persist Corp"},
            "is_relevant": False,
        }

        created_job = repository.create(job_data)

        # Force reload from database
        db_session.expire_all()

        retrieved_job = repository.get_by_external_id("2004")
        assert retrieved_job is not None
        assert retrieved_job.is_relevant is False
        assert retrieved_job.id == created_job.id

    def test_create_job_with_full_data_and_is_relevant_false(self, repository, sample_job_dict):
        """Test creating a job with full data and is_relevant=False."""
        job_data = sample_job_dict.copy()
        job_data["job_id"] = 2005
        job_data["url"] = "https://example.com/jobs/2005"
        job_data["is_relevant"] = False

        job = repository.create(job_data)

        assert job.id is not None
        assert job.title == "Senior Python Developer"
        assert job.is_relevant is False
        assert job.company_rel is not None

    def test_create_job_with_full_data_and_is_relevant_true(self, repository, sample_job_dict):
        """Test creating a job with full data and is_relevant=True."""
        job_data = sample_job_dict.copy()
        job_data["job_id"] = 2006
        job_data["url"] = "https://example.com/jobs/2006"
        job_data["is_relevant"] = True

        job = repository.create(job_data)

        assert job.id is not None
        assert job.title == "Senior Python Developer"
        assert job.is_relevant is True


class TestJobRepositoryIsFiltered:
    """Tests for JobRepository is_filtered field handling.

    These tests verify the NEW behavior where jobs can be created with
    is_filtered=True to indicate they were rejected by pre-LLM filtering.
    """

    @pytest.fixture
    def repository(self, reference_data_service, job_mapper, db_session):
        """Create a JobRepository instance."""
        return JobRepository(reference_data_service, job_mapper, db_session)

    def test_create_job_with_is_filtered_true(self, repository):
        """Test creating a job with is_filtered=True."""
        job_data = {
            "job_id": 3001,
            "title": "Filtered Job",
            "company": {"name": "Filtered Corp"},
            "is_filtered": True,
            "is_relevant": False,
        }

        job = repository.create(job_data)

        assert job.id is not None
        assert job.is_filtered is True
        assert job.is_relevant is False

    def test_create_job_with_is_filtered_false(self, repository):
        """Test creating a job with is_filtered=False (default behavior)."""
        job_data = {
            "job_id": 3002,
            "title": "Non-filtered Job",
            "company": {"name": "Normal Corp"},
            "is_filtered": False,
        }

        job = repository.create(job_data)

        assert job.id is not None
        assert job.is_filtered is False

    def test_create_job_defaults_is_filtered_to_false(self, repository):
        """Test that is_filtered defaults to False when not specified."""
        job_data = {
            "job_id": 3003,
            "title": "Default Filtered Job",
            "company": {"name": "Default Corp"},
        }

        job = repository.create(job_data)

        assert job.id is not None
        assert job.is_filtered is False

    def test_create_job_is_filtered_persists_correctly(self, repository, db_session):
        """Test that is_filtered value is correctly persisted to database."""
        job_data = {
            "job_id": 3004,
            "title": "Persisted Filtered Job",
            "company": {"name": "Persist Corp"},
            "is_filtered": True,
            "is_relevant": False,
        }

        created_job = repository.create(job_data)

        # Force reload from database
        db_session.expire_all()

        retrieved_job = repository.get_by_external_id("3004")
        assert retrieved_job is not None
        assert retrieved_job.is_filtered is True
        assert retrieved_job.is_relevant is False
        assert retrieved_job.id == created_job.id


class TestJobRepositorySaveFilteredJobs:
    """Tests for save_filtered_jobs method.

    These tests verify the NEW method that saves multiple filtered jobs
    in a single batch operation with correct flags (is_filtered=True, is_relevant=False).
    """

    @pytest.fixture
    def repository(self, reference_data_service, job_mapper, db_session):
        """Create a JobRepository instance."""
        return JobRepository(reference_data_service, job_mapper, db_session)

    def test_save_filtered_jobs_persists_with_correct_flags(self, repository, db_session):
        """Test that save_filtered_jobs stores jobs with is_filtered=True, is_relevant=False.

        The primary purpose of this method is to store filtered jobs with the
        correct flags so they are included in existing_urls for future scrapes.
        """
        filtered_jobs = [
            {
                "job_id": 4001,
                "title": "Filtered Job 1",
                "url": "https://example.com/jobs/4001",
                "source": "djinni",
                "company": {"name": "Company A"},
                "experience_months": 120,
                "location": {"can_apply": True},
            },
            {
                "job_id": 4002,
                "title": "Filtered Job 2",
                "url": "https://example.com/jobs/4002",
                "source": "djinni",
                "company": {"name": "Company B"},
                "experience_months": 80,
                "location": {"can_apply": False},
            },
        ]

        count = repository.save_filtered_jobs(filtered_jobs)

        assert count == 2

        job1 = repository.get_by_external_id("4001")
        assert job1 is not None
        assert job1.is_filtered is True
        assert job1.is_relevant is False

        job2 = repository.get_by_external_id("4002")
        assert job2 is not None
        assert job2.is_filtered is True
        assert job2.is_relevant is False

    def test_save_filtered_jobs_skips_duplicates_by_external_id(self, repository):
        """Test that save_filtered_jobs skips jobs that already exist by external_id."""
        # Create an existing job first
        existing_job_data = {
            "job_id": 4003,
            "title": "Existing Job",
            "url": "https://example.com/jobs/4003",
            "source": "djinni",
            "company": {"name": "Existing Corp"},
        }
        repository.create(existing_job_data)

        # Try to save filtered jobs including the duplicate
        filtered_jobs = [
            {
                "job_id": 4003,  # Duplicate!
                "title": "Duplicate Job",
                "url": "https://example.com/jobs/4003-duplicate",
                "source": "djinni",
                "company": {"name": "Company A"},
            },
            {
                "job_id": 4004,
                "title": "New Filtered Job",
                "url": "https://example.com/jobs/4004",
                "source": "djinni",
                "company": {"name": "Company B"},
            },
        ]

        count = repository.save_filtered_jobs(filtered_jobs)

        # Only the new job should be saved
        assert count == 1

        # Verify the new job was saved
        new_job = repository.get_by_external_id("4004")
        assert new_job is not None
        assert new_job.is_filtered is True

    def test_save_filtered_jobs_skips_duplicates_by_source_url(self, repository):
        """Test that save_filtered_jobs skips jobs that already exist by source_url."""
        # Create an existing job first
        existing_job_data = {
            "job_id": 4005,
            "title": "Existing Job",
            "url": "https://example.com/jobs/same-url",
            "source": "djinni",
            "company": {"name": "Existing Corp"},
        }
        repository.create(existing_job_data)

        # Try to save filtered jobs with same URL but different external_id
        filtered_jobs = [
            {
                "job_id": 4006,  # Different external_id
                "title": "Duplicate URL Job",
                "url": "https://example.com/jobs/same-url",  # Same URL!
                "source": "djinni",
                "company": {"name": "Company A"},
            },
            {
                "job_id": 4007,
                "title": "New Filtered Job",
                "url": "https://example.com/jobs/4007",
                "source": "djinni",
                "company": {"name": "Company B"},
            },
        ]

        count = repository.save_filtered_jobs(filtered_jobs)

        # Only the new job should be saved
        assert count == 1

    def test_save_filtered_jobs_returns_count_of_saved_jobs(self, repository):
        """Test that save_filtered_jobs returns the correct count of saved jobs."""
        filtered_jobs = [
            {"job_id": 4008, "title": "Job 1", "url": "https://example.com/1", "source": "djinni"},
            {"job_id": 4009, "title": "Job 2", "url": "https://example.com/2", "source": "djinni"},
            {"job_id": 4010, "title": "Job 3", "url": "https://example.com/3", "source": "djinni"},
        ]

        count = repository.save_filtered_jobs(filtered_jobs)

        assert count == 3

    def test_save_filtered_jobs_with_empty_list_returns_zero(self, repository):
        """Test that save_filtered_jobs with empty list returns 0."""
        count = repository.save_filtered_jobs([])

        assert count == 0

    def test_save_filtered_jobs_stores_source_url_for_existing_urls(self, repository, db_session):
        """Test that saved filtered jobs have source_url set for get_existing_urls_by_source."""
        filtered_jobs = [
            {
                "job_id": 4011,
                "title": "Filtered Job",
                "url": "https://djinni.co/jobs/4011",
                "source": "djinni",
            },
        ]

        repository.save_filtered_jobs(filtered_jobs)

        # The URL should be retrievable via get_existing_urls_by_source
        urls = repository.get_existing_urls_by_source("djinni")
        assert "https://djinni.co/jobs/4011" in urls


class TestJobRepositoryGetExistingUrlsIncludesFiltered:
    """Tests for get_existing_urls_by_source including filtered jobs.

    These tests verify that get_existing_urls_by_source returns URLs
    for filtered jobs (is_filtered=True) to prevent re-fetching.
    """

    @pytest.fixture
    def repository(self, reference_data_service, job_mapper, db_session):
        """Create a JobRepository instance."""
        return JobRepository(reference_data_service, job_mapper, db_session)

    def test_get_existing_urls_includes_filtered_jobs(self, repository, db_session):
        """Test that get_existing_urls_by_source includes URLs of filtered jobs.

        Filtered jobs should be included in existing_urls to prevent
        the scrapper from re-fetching them.
        """
        from datetime import datetime, UTC

        posted_at = datetime.now(UTC)
        if not getattr(Job.__table__.c.posted_at.type, "timezone", False):
            posted_at = posted_at.replace(tzinfo=None)

        # Create a regular job
        regular_job = Job(
            title="Regular Job",
            external_id="urls-filtered-1",
            source="djinni",
            source_url="https://djinni.co/jobs/regular",
            is_filtered=False,
            is_relevant=True,
            posted_at=posted_at,
        )
        # Create a filtered job
        filtered_job = Job(
            title="Filtered Job",
            external_id="urls-filtered-2",
            source="djinni",
            source_url="https://djinni.co/jobs/filtered",
            is_filtered=True,
            is_relevant=False,
            posted_at=posted_at,
        )
        db_session.add_all([regular_job, filtered_job])
        db_session.commit()

        urls = repository.get_existing_urls_by_source("djinni")

        # Both URLs should be included
        assert len(urls) == 2
        assert "https://djinni.co/jobs/regular" in urls
        assert "https://djinni.co/jobs/filtered" in urls

    def test_get_existing_urls_includes_irrelevant_jobs(self, repository, db_session):
        """Test that get_existing_urls_by_source includes URLs of irrelevant jobs.

        Jobs marked as is_relevant=False should still be included in
        existing_urls since they were already processed.
        """
        from datetime import datetime, UTC

        posted_at = datetime.now(UTC)
        if not getattr(Job.__table__.c.posted_at.type, "timezone", False):
            posted_at = posted_at.replace(tzinfo=None)

        # Create an irrelevant (but not filtered) job
        irrelevant_job = Job(
            title="Irrelevant Job",
            external_id="urls-irrelevant-1",
            source="djinni",
            source_url="https://djinni.co/jobs/irrelevant",
            is_filtered=False,
            is_relevant=False,
            posted_at=posted_at,
        )
        db_session.add(irrelevant_job)
        db_session.commit()

        urls = repository.get_existing_urls_by_source("djinni")

        assert "https://djinni.co/jobs/irrelevant" in urls


class TestJobRepositoryGetLatestUpdatedAt:
    """Tests for get_latest_updated_at method."""

    @pytest.fixture
    def repository(self, reference_data_service, job_mapper, db_session):
        """Create a JobRepository instance."""
        return JobRepository(reference_data_service, job_mapper, db_session)

    def test_get_latest_updated_at_returns_none_when_no_jobs_exist(self, repository):
        """Test that get_latest_updated_at returns None when database is empty."""
        result = repository.get_latest_updated_at()

        assert result is None

    def test_get_latest_updated_at_returns_most_recent_timestamp(self, repository, db_session):
        """Test that get_latest_updated_at returns the most recent timestamp."""
        from datetime import datetime, timedelta, UTC

        now = datetime.now(UTC)
        old_time = now - timedelta(days=10)
        recent_time = now - timedelta(days=2)

        # Handle timezone-naive column if needed
        if not getattr(Job.__table__.c.updated_at.type, "timezone", False):
            old_time = old_time.replace(tzinfo=None)
            recent_time = recent_time.replace(tzinfo=None)

        old_job = Job(
            title="Old Job",
            external_id="latest-test-old",
            source="djinni",
        )
        # Manually set updated_at for old job
        db_session.add(old_job)
        db_session.flush()
        db_session.execute(
            Job.__table__.update()
            .where(Job.__table__.c.id == old_job.id)
            .values(updated_at=old_time)
        )

        recent_job = Job(
            title="Recent Job",
            external_id="latest-test-recent",
            source="djinni",
        )
        db_session.add(recent_job)
        db_session.flush()
        db_session.execute(
            Job.__table__.update()
            .where(Job.__table__.c.id == recent_job.id)
            .values(updated_at=recent_time)
        )
        db_session.commit()

        result = repository.get_latest_updated_at()

        assert result is not None
        # Compare without microseconds due to DB precision
        if result.tzinfo is None:
            recent_time_compare = recent_time.replace(tzinfo=None)
        else:
            recent_time_compare = recent_time
        assert abs((result - recent_time_compare).total_seconds()) < 1

    def test_get_latest_updated_at_identifies_correct_timestamp_with_multiple_jobs(
        self, repository, db_session
    ):
        """Test correct identification of latest timestamp across many jobs."""
        from datetime import datetime, timedelta, UTC

        now = datetime.now(UTC)
        timestamps = [
            now - timedelta(days=30),
            now - timedelta(days=15),
            now - timedelta(days=7),
            now - timedelta(days=1),  # This should be the latest
            now - timedelta(days=20),
        ]

        if not getattr(Job.__table__.c.updated_at.type, "timezone", False):
            timestamps = [ts.replace(tzinfo=None) for ts in timestamps]

        for i, ts in enumerate(timestamps):
            job = Job(
                title=f"Job {i}",
                external_id=f"multi-job-{i}",
                source="djinni",
            )
            db_session.add(job)
            db_session.flush()
            db_session.execute(
                Job.__table__.update().where(Job.__table__.c.id == job.id).values(updated_at=ts)
            )
        db_session.commit()

        result = repository.get_latest_updated_at()

        assert result is not None
        expected_latest = timestamps[3]  # days=1 is the most recent
        assert abs((result - expected_latest).total_seconds()) < 1

    def test_get_latest_updated_at_returns_datetime_type(self, repository, db_session):
        """Test that get_latest_updated_at returns a datetime object."""
        from datetime import datetime

        job = Job(
            title="Test Job",
            external_id="datetime-type-test",
            source="djinni",
        )
        db_session.add(job)
        db_session.commit()

        result = repository.get_latest_updated_at()

        assert result is not None
        assert isinstance(result, datetime)
