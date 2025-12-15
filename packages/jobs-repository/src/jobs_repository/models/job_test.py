"""Tests for Job model."""

import pytest
from sqlalchemy.exc import IntegrityError

from jobs_repository.models import Job


class TestJobModelConstraints:
    """Tests for Job model database constraints."""

    def test_title_is_required(self, db_session):
        """Test that title field is required (nullable=False)."""
        job = Job(title=None)
        db_session.add(job)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_external_id_unique_constraint(self, db_session):
        """Test that external_id must be unique."""
        job1 = Job(title="Job 1", external_id="unique-id-123")
        db_session.add(job1)
        db_session.commit()

        job2 = Job(title="Job 2", external_id="unique-id-123")
        db_session.add(job2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_multiple_jobs_can_have_none_external_id(self, db_session):
        """Test that multiple jobs can have None external_id."""
        job1 = Job(title="Job 1", external_id=None)
        job2 = Job(title="Job 2", external_id=None)
        db_session.add_all([job1, job2])
        db_session.commit()

        assert job1.id is not None
        assert job2.id is not None
        assert job1.id != job2.id


class TestJobModelEdgeCases:
    """Edge case tests for Job model."""

    def test_special_characters_in_title(self, db_session):
        """Test that special characters in title are preserved."""
        special_title = "Senior Developer (C/C++) - Remote <script>alert('xss')</script>"
        job = Job(title=special_title)
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.title == special_title

    def test_unicode_characters_in_fields(self, db_session):
        """Test that unicode characters are properly stored."""
        job = Job(
            title="ソフトウェアエンジニア",
            description="日本語の説明",
            source="日本",
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.title == "ソフトウェアエンジニア"
        assert job.description == "日本語の説明"
        assert job.source == "日本"

    def test_skills_with_special_characters(self, db_session):
        """Test that skills with special characters are preserved."""
        skills = ["C++", "C#", "Node.js", "AWS/GCP", "React/Vue"]
        job = Job(title="Test Job", must_have_skills=skills)
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.must_have_skills == skills


class TestJobModelIsRelevant:
    """Tests for Job model is_relevant field."""

    def test_is_relevant_defaults_to_true(self, db_session):
        """Test that is_relevant defaults to True when not specified."""
        job = Job(title="Test Job", external_id="is-relevant-default-1")
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.is_relevant is True

    def test_is_relevant_accepts_explicit_true(self, db_session):
        """Test that is_relevant can be explicitly set to True."""
        job = Job(title="Test Job", external_id="is-relevant-true-1", is_relevant=True)
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.is_relevant is True

    def test_is_relevant_accepts_explicit_false(self, db_session):
        """Test that is_relevant can be explicitly set to False."""
        job = Job(title="Test Job", external_id="is-relevant-false-1", is_relevant=False)
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.is_relevant is False

    def test_is_relevant_column_is_defined_as_non_nullable(self, db_session):
        """Test that is_relevant column is defined as non-nullable in the model."""
        # Verify the column definition itself (SQLite with defaults applies defaults
        # at Python level, so we test the model definition instead of runtime behavior)
        is_relevant_column = Job.__table__.c.is_relevant
        assert is_relevant_column.nullable is False
        assert is_relevant_column.default.arg is True

    def test_is_relevant_persists_false_value_correctly(self, db_session):
        """Test that False value for is_relevant is persisted and retrieved correctly."""
        job = Job(title="Irrelevant Job", external_id="is-relevant-persist-1", is_relevant=False)
        db_session.add(job)
        db_session.commit()

        # Clear session cache to force reload from database
        db_session.expire_all()

        retrieved_job = db_session.query(Job).filter_by(external_id="is-relevant-persist-1").first()
        assert retrieved_job is not None
        assert retrieved_job.is_relevant is False

    def test_is_relevant_persists_true_value_correctly(self, db_session):
        """Test that True value for is_relevant is persisted and retrieved correctly."""
        job = Job(title="Relevant Job", external_id="is-relevant-persist-2", is_relevant=True)
        db_session.add(job)
        db_session.commit()

        # Clear session cache to force reload from database
        db_session.expire_all()

        retrieved_job = db_session.query(Job).filter_by(external_id="is-relevant-persist-2").first()
        assert retrieved_job is not None
        assert retrieved_job.is_relevant is True


class TestJobModelIsFiltered:
    """Tests for Job model is_filtered field.

    These tests verify the NEW behavior where jobs can be marked as filtered
    (is_filtered=True) to indicate they failed pre-LLM filtering criteria.
    Filtered jobs should be stored to prevent re-fetching from scrappers.
    """

    def test_is_filtered_attribute_exists(self, db_session):
        """Test that Job model has is_filtered attribute.

        The is_filtered field should exist on the Job model to track
        jobs that were rejected by pre-LLM filtering.
        """
        job = Job(title="Test Job", external_id="is-filtered-exists-1")
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        # This test will fail until is_filtered column is added to the model
        assert hasattr(job, "is_filtered")

    def test_is_filtered_defaults_to_false(self, db_session):
        """Test that is_filtered defaults to False when not specified.

        By default, jobs should not be marked as filtered.
        """
        job = Job(title="Test Job", external_id="is-filtered-default-1")
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.is_filtered is False

    def test_is_filtered_accepts_explicit_true(self, db_session):
        """Test that is_filtered can be explicitly set to True.

        Jobs that fail filtering should be stored with is_filtered=True.
        """
        job = Job(title="Filtered Job", external_id="is-filtered-true-1", is_filtered=True)
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.is_filtered is True

    def test_is_filtered_accepts_explicit_false(self, db_session):
        """Test that is_filtered can be explicitly set to False."""
        job = Job(title="Non-filtered Job", external_id="is-filtered-false-1", is_filtered=False)
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.is_filtered is False

    def test_is_filtered_column_is_defined_as_non_nullable(self, db_session):
        """Test that is_filtered column is defined as non-nullable in the model."""
        is_filtered_column = Job.__table__.c.is_filtered
        assert is_filtered_column.nullable is False
        assert is_filtered_column.default.arg is False

    def test_is_filtered_persists_true_value_correctly(self, db_session):
        """Test that True value for is_filtered is persisted and retrieved correctly."""
        job = Job(title="Filtered Job", external_id="is-filtered-persist-1", is_filtered=True)
        db_session.add(job)
        db_session.commit()

        # Clear session cache to force reload from database
        db_session.expire_all()

        retrieved_job = db_session.query(Job).filter_by(external_id="is-filtered-persist-1").first()
        assert retrieved_job is not None
        assert retrieved_job.is_filtered is True

    def test_is_filtered_persists_false_value_correctly(self, db_session):
        """Test that False value for is_filtered is persisted and retrieved correctly."""
        job = Job(title="Non-filtered Job", external_id="is-filtered-persist-2", is_filtered=False)
        db_session.add(job)
        db_session.commit()

        # Clear session cache to force reload from database
        db_session.expire_all()

        retrieved_job = db_session.query(Job).filter_by(external_id="is-filtered-persist-2").first()
        assert retrieved_job is not None
        assert retrieved_job.is_filtered is False

    def test_filtered_job_has_is_relevant_false(self, db_session):
        """Test that a filtered job should have is_relevant=False.

        Filtered jobs are by definition not relevant and should be stored
        with is_filtered=True and is_relevant=False.
        """
        job = Job(
            title="Filtered Irrelevant Job",
            external_id="is-filtered-relevant-1",
            is_filtered=True,
            is_relevant=False,
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.is_filtered is True
        assert job.is_relevant is False
