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
