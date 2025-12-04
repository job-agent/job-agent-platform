"""Tests for Company model."""

from jobs_repository.models import Job, Company


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
