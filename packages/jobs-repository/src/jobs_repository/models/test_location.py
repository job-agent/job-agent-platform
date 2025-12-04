"""Tests for Location model."""

from jobs_repository.models import Job, Location


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
