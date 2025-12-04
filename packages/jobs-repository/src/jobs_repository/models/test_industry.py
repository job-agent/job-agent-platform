"""Tests for Industry model."""

from jobs_repository.models import Job, Industry


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
