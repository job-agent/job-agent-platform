"""Tests for database models."""

from datetime import datetime, UTC

import pytest

from jobs_repository.models import Job, Company, Location, Category, Industry


class TestCompanyModel:
    """Test suite for Company model."""

    def test_repr(self, db_session):
        """Test Company __repr__ method."""
        company = Company(name="Test Corp")
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)

        repr_str = repr(company)

        assert "Company" in repr_str
        assert "Test Corp" in repr_str
        assert str(company.id) in repr_str

    def test_repr_without_id(self):
        """Test Company __repr__ before persistence."""
        company = Company(name="Test Corp")

        repr_str = repr(company)

        assert "Company" in repr_str
        assert "Test Corp" in repr_str

    def test_name_field(self, db_session):
        """Test Company name field."""
        company = Company(name="Example Company")
        db_session.add(company)
        db_session.commit()

        assert company.name == "Example Company"

    def test_website_field(self, db_session):
        """Test Company website field."""
        company = Company(name="Example Company", website="https://example.com")
        db_session.add(company)
        db_session.commit()

        assert company.website == "https://example.com"

    def test_website_optional(self, db_session):
        """Test that Company website is optional."""
        company = Company(name="Example Company")
        db_session.add(company)
        db_session.commit()

        assert company.website is None

    def test_jobs_relationship(self, db_session, sample_company):
        """Test Company jobs relationship."""
        job = Job(title="Test Job", company_id=sample_company.id)
        db_session.add(job)
        db_session.commit()

        assert len(sample_company.jobs) == 1
        assert sample_company.jobs[0].title == "Test Job"


class TestLocationModel:
    """Test suite for Location model."""

    def test_repr(self, db_session):
        """Test Location __repr__ method."""
        location = Location(region="San Francisco, CA")
        db_session.add(location)
        db_session.commit()
        db_session.refresh(location)

        repr_str = repr(location)

        assert "Location" in repr_str
        assert "San Francisco, CA" in repr_str
        assert str(location.id) in repr_str

    def test_repr_without_id(self):
        """Test Location __repr__ before persistence."""
        location = Location(region="New York, NY")

        repr_str = repr(location)

        assert "Location" in repr_str
        assert "New York, NY" in repr_str

    def test_region_field(self, db_session):
        """Test Location region field."""
        location = Location(region="Seattle, WA")
        db_session.add(location)
        db_session.commit()

        assert location.region == "Seattle, WA"

    def test_jobs_relationship(self, db_session, sample_location):
        """Test Location jobs relationship."""
        job = Job(title="Test Job", location_id=sample_location.id)
        db_session.add(job)
        db_session.commit()

        assert len(sample_location.jobs) == 1
        assert sample_location.jobs[0].title == "Test Job"


class TestCategoryModel:
    """Test suite for Category model."""

    def test_repr(self, db_session):
        """Test Category __repr__ method."""
        category = Category(name="Engineering")
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        repr_str = repr(category)

        assert "Category" in repr_str
        assert "Engineering" in repr_str
        assert str(category.id) in repr_str

    def test_repr_without_id(self):
        """Test Category __repr__ before persistence."""
        category = Category(name="Design")

        repr_str = repr(category)

        assert "Category" in repr_str
        assert "Design" in repr_str

    def test_name_field(self, db_session):
        """Test Category name field."""
        category = Category(name="Data Science")
        db_session.add(category)
        db_session.commit()

        assert category.name == "Data Science"

    def test_jobs_relationship(self, db_session, sample_category):
        """Test Category jobs relationship."""
        job = Job(title="Test Job", category_id=sample_category.id)
        db_session.add(job)
        db_session.commit()

        assert len(sample_category.jobs) == 1
        assert sample_category.jobs[0].title == "Test Job"


class TestIndustryModel:
    """Test suite for Industry model."""

    def test_repr(self, db_session):
        """Test Industry __repr__ method."""
        industry = Industry(name="Technology")
        db_session.add(industry)
        db_session.commit()
        db_session.refresh(industry)

        repr_str = repr(industry)

        assert "Industry" in repr_str
        assert "Technology" in repr_str
        assert str(industry.id) in repr_str

    def test_repr_without_id(self):
        """Test Industry __repr__ before persistence."""
        industry = Industry(name="Finance")

        repr_str = repr(industry)

        assert "Industry" in repr_str
        assert "Finance" in repr_str

    def test_name_field(self, db_session):
        """Test Industry name field."""
        industry = Industry(name="Healthcare")
        db_session.add(industry)
        db_session.commit()

        assert industry.name == "Healthcare"

    def test_jobs_relationship(self, db_session, sample_industry):
        """Test Industry jobs relationship."""
        job = Job(title="Test Job", industry_id=sample_industry.id)
        db_session.add(job)
        db_session.commit()

        assert len(sample_industry.jobs) == 1
        assert sample_industry.jobs[0].title == "Test Job"


class TestJobModel:
    """Test suite for Job model."""

    def test_repr_with_company(self, db_session, sample_company):
        """Test Job __repr__ with company relationship."""
        job = Job(title="Software Engineer", company_id=sample_company.id)
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        repr_str = repr(job)

        assert "Job" in repr_str
        assert "Software Engineer" in repr_str
        assert sample_company.name in repr_str
        assert str(job.id) in repr_str

    def test_repr_without_company(self, db_session):
        """Test Job __repr__ without company."""
        job = Job(title="Software Engineer")
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        repr_str = repr(job)

        assert "Job" in repr_str
        assert "Software Engineer" in repr_str
        assert "Unknown" in repr_str

    def test_to_dict_with_all_relationships(self, sample_job):
        """Test Job to_dict with all relationships populated."""
        job_dict = sample_job.to_dict()

        assert job_dict["id"] == sample_job.id
        assert job_dict["title"] == "Software Engineer"
        assert job_dict["description"] == "We are looking for a talented software engineer."
        assert job_dict["company_id"] == sample_job.company_id
        assert job_dict["company_name"] == "Tech Corp"
        assert job_dict["location_id"] == sample_job.location_id
        assert job_dict["location_region"] == "San Francisco, CA"
        assert job_dict["category_id"] == sample_job.category_id
        assert job_dict["category_name"] == "Software Engineering"
        assert job_dict["industry_id"] == sample_job.industry_id
        assert job_dict["industry_name"] == "Technology"
        assert job_dict["must_have_skills"] == ["Python", "SQL"]
        assert job_dict["nice_to_have_skills"] == ["Docker", "Kubernetes"]
        assert job_dict["job_type"] == "Full-time"
        assert job_dict["experience_months"] == 24
        assert job_dict["salary_min"] == 100000.0
        assert job_dict["salary_max"] == 150000.0
        assert job_dict["salary_currency"] == "USD"
        assert job_dict["external_id"] == "job-123"
        assert job_dict["source"] == "LinkedIn"
        assert job_dict["source_url"] == "https://linkedin.com/jobs/123"
        assert job_dict["is_remote"] is False

    def test_to_dict_without_relationships(self, db_session):
        """Test Job to_dict without any relationships."""
        job = Job(title="Standalone Job")
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        job_dict = job.to_dict()

        assert job_dict["id"] == job.id
        assert job_dict["title"] == "Standalone Job"
        assert job_dict["company_id"] is None
        assert job_dict["company_name"] is None
        assert job_dict["location_id"] is None
        assert job_dict["location_region"] is None
        assert job_dict["category_id"] is None
        assert job_dict["category_name"] is None
        assert job_dict["industry_id"] is None
        assert job_dict["industry_name"] is None

    def test_to_dict_with_partial_relationships(self, db_session, sample_company):
        """Test Job to_dict with only some relationships."""
        job = Job(title="Test Job", company_id=sample_company.id)
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        job_dict = job.to_dict()

        assert job_dict["company_id"] == sample_company.id
        assert job_dict["company_name"] == sample_company.name
        assert job_dict["location_id"] is None
        assert job_dict["location_region"] is None

    def test_to_dict_datetime_serialization(self, sample_job):
        """Test that datetime fields are serialized to ISO format."""
        job_dict = sample_job.to_dict()

        assert isinstance(job_dict["posted_at"], str)
        assert isinstance(job_dict["expires_at"], str)
        assert isinstance(job_dict["created_at"], str)
        assert isinstance(job_dict["updated_at"], str)
        assert "2024-01-01" in job_dict["posted_at"]
        assert "2024-02-01" in job_dict["expires_at"]

    def test_to_dict_with_none_datetimes(self, db_session):
        """Test to_dict with None datetime fields."""
        job = Job(title="Test Job")
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        job_dict = job.to_dict()

        assert job_dict["posted_at"] is None
        assert job_dict["expires_at"] is None
        assert job_dict["created_at"] is not None
        assert job_dict["updated_at"] is not None

    def test_to_dict_includes_all_fields(self, sample_job):
        """Test that to_dict includes all expected fields."""
        job_dict = sample_job.to_dict()

        expected_fields = [
            "id",
            "title",
            "company_id",
            "company_name",
            "location_id",
            "location_region",
            "category_id",
            "category_name",
            "industry_id",
            "industry_name",
            "description",
            "must_have_skills",
            "nice_to_have_skills",
            "job_type",
            "experience_months",
            "salary_min",
            "salary_max",
            "salary_currency",
            "external_id",
            "source",
            "source_url",
            "is_remote",
            "posted_at",
            "expires_at",
            "created_at",
            "updated_at",
        ]

        for field in expected_fields:
            assert field in job_dict

    def test_created_at_auto_populated(self, db_session):
        """Test that created_at is automatically populated."""
        job = Job(title="Test Job")
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.created_at is not None
        assert isinstance(job.created_at, datetime)

    def test_updated_at_auto_populated(self, db_session):
        """Test that updated_at is automatically populated."""
        job = Job(title="Test Job")
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.updated_at is not None
        assert isinstance(job.updated_at, datetime)

    def test_skills_arrays(self, db_session):
        """Test that skills arrays work correctly."""
        job = Job(
            title="Test Job",
            must_have_skills=["Python", "SQL"],
            nice_to_have_skills=["Docker"],
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.must_have_skills == ["Python", "SQL"]
        assert job.nice_to_have_skills == ["Docker"]

    def test_nullable_fields(self, db_session):
        """Test that nullable fields can be None."""
        job = Job(title="Test Job")
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.description is None
        assert job.company_id is None
        assert job.location_id is None
        assert job.category_id is None
        assert job.industry_id is None
        assert job.job_type is None
        assert job.experience_months is None
        assert job.salary_min is None
        assert job.salary_max is None
        assert job.external_id is None
        assert job.source is None
        assert job.source_url is None
        assert job.posted_at is None
        assert job.expires_at is None

    def test_relationships_lazy_loading(self, sample_job):
        """Test that relationships support lazy loading."""
        assert sample_job.company_rel is not None
        assert sample_job.location_rel is not None
        assert sample_job.category_rel is not None
        assert sample_job.industry_rel is not None

        assert sample_job.company_rel.name == "Tech Corp"
        assert sample_job.location_rel.region == "San Francisco, CA"
        assert sample_job.category_rel.name == "Software Engineering"
        assert sample_job.industry_rel.name == "Technology"

    def test_salary_currency_defaults_to_usd(self, db_session):
        """Test that salary_currency defaults to USD."""
        job = Job(title="Test Job", salary_min=50000.0)
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.salary_currency == "USD"

    def test_is_remote_defaults_to_false(self, db_session):
        """Test that is_remote defaults to False."""
        job = Job(title="Test Job")
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.is_remote is False
