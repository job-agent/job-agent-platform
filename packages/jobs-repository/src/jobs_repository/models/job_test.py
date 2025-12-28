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


class TestJobModelWith2DSkillStructure:
    """Tests for Job model with 2D skill structure.

    These tests verify that skills are stored as 2D lists (JSONB):
    - Outer list: AND relationships (all groups required)
    - Inner lists: OR relationships (alternatives within a group)
    """

    def test_stores_2d_must_have_skills(self, db_session):
        """Test that 2D must-have skills are stored correctly."""
        skills_2d = [["Python"], ["Django"], ["PostgreSQL"]]
        job = Job(title="Test Job", external_id="2d-skills-1", must_have_skills=skills_2d)
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.must_have_skills == [["Python"], ["Django"], ["PostgreSQL"]]

    def test_stores_2d_nice_to_have_skills(self, db_session):
        """Test that 2D nice-to-have skills are stored correctly."""
        skills_2d = [["Docker"], ["Kubernetes"], ["AWS"]]
        job = Job(title="Test Job", external_id="2d-skills-2", nice_to_have_skills=skills_2d)
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.nice_to_have_skills == [["Docker"], ["Kubernetes"], ["AWS"]]

    def test_stores_or_groups_in_skills(self, db_session):
        """Test that OR groups (inner lists with multiple skills) are stored."""
        skills_2d = [["JavaScript", "Python"], ["React"]]
        job = Job(title="Test Job", external_id="2d-skills-3", must_have_skills=skills_2d)
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.must_have_skills == [["JavaScript", "Python"], ["React"]]

    def test_stores_mixed_solo_and_or_groups(self, db_session):
        """Test that mixed solo skills and OR groups are stored."""
        skills_2d = [["JavaScript", "TypeScript"], ["React"], ["PostgreSQL", "MySQL"]]
        job = Job(title="Test Job", external_id="2d-skills-4", must_have_skills=skills_2d)
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.must_have_skills == [
            ["JavaScript", "TypeScript"],
            ["React"],
            ["PostgreSQL", "MySQL"],
        ]

    def test_stores_empty_2d_skill_list(self, db_session):
        """Test that empty 2D skill list is stored correctly."""
        job = Job(title="Test Job", external_id="2d-skills-5", must_have_skills=[])
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.must_have_skills == []

    def test_retrieves_2d_skills_after_session_clear(self, db_session):
        """Test that 2D skills are retrieved correctly after session clear."""
        skills_2d = [["A", "B"], ["C"], ["D", "E", "F"]]
        job = Job(title="Test Job", external_id="2d-skills-6", must_have_skills=skills_2d)
        db_session.add(job)
        db_session.commit()

        # Clear session cache to force reload from database
        db_session.expire_all()

        retrieved_job = db_session.query(Job).filter_by(external_id="2d-skills-6").first()
        assert retrieved_job is not None
        assert retrieved_job.must_have_skills == [["A", "B"], ["C"], ["D", "E", "F"]]

    def test_stores_skills_with_special_characters(self, db_session):
        """Test that skills with special characters are preserved in 2D format."""
        skills_2d = [["C++", "C#"], ["Node.js"], ["AWS/GCP"]]
        job = Job(title="Test Job", external_id="2d-skills-7", must_have_skills=skills_2d)
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.must_have_skills == [["C++", "C#"], ["Node.js"], ["AWS/GCP"]]

    def test_preserves_skill_group_order(self, db_session):
        """Test that order of skill groups is preserved."""
        skills_2d = [["Z"], ["Y"], ["X"]]
        job = Job(title="Test Job", external_id="2d-skills-8", must_have_skills=skills_2d)
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.must_have_skills == [["Z"], ["Y"], ["X"]]

    def test_preserves_alternatives_order_within_groups(self, db_session):
        """Test that order of alternatives within groups is preserved."""
        skills_2d = [["C", "B", "A"]]
        job = Job(title="Test Job", external_id="2d-skills-9", must_have_skills=skills_2d)
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.must_have_skills[0] == ["C", "B", "A"]

    def test_both_skill_fields_use_2d_structure(self, db_session):
        """Test that both must-have and nice-to-have skills use 2D structure."""
        must_have = [["Python", "Java"], ["Django"]]
        nice_to_have = [["Docker", "Kubernetes"], ["AWS"]]
        job = Job(
            title="Test Job",
            external_id="2d-skills-10",
            must_have_skills=must_have,
            nice_to_have_skills=nice_to_have,
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.must_have_skills == [["Python", "Java"], ["Django"]]
        assert job.nice_to_have_skills == [["Docker", "Kubernetes"], ["AWS"]]
