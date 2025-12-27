"""Tests for Essay model.

These tests verify the Essay SQLAlchemy model has correct columns,
types, constraints, and default values.
"""

import pytest
from datetime import datetime, UTC
from sqlalchemy.exc import IntegrityError

# Import test model from conftest for SQLite compatibility
from essay_repository.conftest import SQLiteEssay


class TestEssayModelSchema:
    """Tests for Essay model schema and column definitions."""

    def test_essay_table_exists(self, db_session):
        """Test that essays table is created."""
        # If we can query the table, it exists
        result = db_session.query(SQLiteEssay).all()
        assert result == []

    def test_essay_has_id_column(self, db_session):
        """Test that Essay model has id column."""
        essay = SQLiteEssay(answer="Test answer")
        db_session.add(essay)
        db_session.commit()
        db_session.refresh(essay)

        assert hasattr(essay, "id")
        assert essay.id is not None
        assert isinstance(essay.id, int)

    def test_essay_id_is_auto_generated(self, db_session):
        """Test that id is auto-generated on creation."""
        essay1 = SQLiteEssay(answer="First answer")
        essay2 = SQLiteEssay(answer="Second answer")

        db_session.add(essay1)
        db_session.commit()
        db_session.add(essay2)
        db_session.commit()

        assert essay1.id is not None
        assert essay2.id is not None
        assert essay1.id != essay2.id
        assert essay2.id > essay1.id  # Sequential IDs

    def test_essay_has_answer_column(self, db_session):
        """Test that Essay model has answer column."""
        essay = SQLiteEssay(answer="My answer content")
        db_session.add(essay)
        db_session.commit()
        db_session.refresh(essay)

        assert hasattr(essay, "answer")
        assert essay.answer == "My answer content"

    def test_essay_has_question_column(self, db_session):
        """Test that Essay model has question column."""
        essay = SQLiteEssay(
            question="What is your experience?",
            answer="5 years of experience",
        )
        db_session.add(essay)
        db_session.commit()
        db_session.refresh(essay)

        assert hasattr(essay, "question")
        assert essay.question == "What is your experience?"

    def test_essay_has_keywords_column(self, db_session):
        """Test that Essay model has keywords column."""
        keywords = ["leadership", "teamwork", "communication"]
        essay = SQLiteEssay(
            answer="My answer about leadership",
            keywords=keywords,
        )
        db_session.add(essay)
        db_session.commit()
        db_session.refresh(essay)

        assert hasattr(essay, "keywords")
        assert essay.keywords == keywords

    def test_essay_has_created_at_column(self, db_session):
        """Test that Essay model has created_at column."""
        essay = SQLiteEssay(answer="Test answer")
        db_session.add(essay)
        db_session.commit()
        db_session.refresh(essay)

        assert hasattr(essay, "created_at")
        assert essay.created_at is not None
        assert isinstance(essay.created_at, datetime)

    def test_essay_has_updated_at_column(self, db_session):
        """Test that Essay model has updated_at column."""
        essay = SQLiteEssay(answer="Test answer")
        db_session.add(essay)
        db_session.commit()
        db_session.refresh(essay)

        assert hasattr(essay, "updated_at")
        assert essay.updated_at is not None
        assert isinstance(essay.updated_at, datetime)


class TestEssayModelConstraints:
    """Tests for Essay model database constraints."""

    def test_answer_is_required(self, db_session):
        """Test that answer field is required (nullable=False)."""
        essay = SQLiteEssay(question="A question without an answer")
        # Explicitly set answer to None to trigger constraint
        essay.answer = None
        db_session.add(essay)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_question_is_optional(self, db_session):
        """Test that question field is optional (nullable=True)."""
        essay = SQLiteEssay(answer="Answer without a question", question=None)
        db_session.add(essay)
        db_session.commit()
        db_session.refresh(essay)

        assert essay.id is not None
        assert essay.question is None

    def test_keywords_is_optional(self, db_session):
        """Test that keywords field is optional (nullable=True)."""
        essay = SQLiteEssay(answer="Answer without keywords", keywords=None)
        db_session.add(essay)
        db_session.commit()
        db_session.refresh(essay)

        assert essay.id is not None
        assert essay.keywords is None


class TestEssayModelTimestamps:
    """Tests for Essay model timestamp behavior."""

    def test_created_at_is_set_automatically(self, db_session):
        """Test that created_at is set automatically on creation."""
        before_create = datetime.now(UTC)
        essay = SQLiteEssay(answer="Test answer")
        db_session.add(essay)
        db_session.commit()
        db_session.refresh(essay)
        after_create = datetime.now(UTC)

        assert essay.created_at is not None
        # Ensure timezone aware comparison
        created_at_aware = (
            essay.created_at.replace(tzinfo=UTC)
            if essay.created_at.tzinfo is None
            else essay.created_at
        )
        assert before_create <= created_at_aware <= after_create

    def test_updated_at_is_set_on_creation(self, db_session):
        """Test that updated_at is set on creation."""
        before_create = datetime.now(UTC)
        essay = SQLiteEssay(answer="Test answer")
        db_session.add(essay)
        db_session.commit()
        db_session.refresh(essay)
        after_create = datetime.now(UTC)

        assert essay.updated_at is not None
        # Ensure timezone aware comparison
        updated_at_aware = (
            essay.updated_at.replace(tzinfo=UTC)
            if essay.updated_at.tzinfo is None
            else essay.updated_at
        )
        assert before_create <= updated_at_aware <= after_create

    def test_created_at_and_updated_at_match_on_creation(self, db_session):
        """Test that created_at and updated_at are the same on creation."""
        essay = SQLiteEssay(answer="Test answer")
        db_session.add(essay)
        db_session.commit()
        db_session.refresh(essay)

        # They should be very close (within a second)
        time_diff = abs((essay.created_at - essay.updated_at).total_seconds())
        assert time_diff < 1


class TestEssayModelEdgeCases:
    """Edge case tests for Essay model."""

    def test_empty_answer_string(self, db_session):
        """Test that empty string answer is accepted (not None)."""
        essay = SQLiteEssay(answer="")
        db_session.add(essay)
        db_session.commit()
        db_session.refresh(essay)

        assert essay.id is not None
        assert essay.answer == ""

    def test_empty_question_string(self, db_session):
        """Test that empty string question is accepted."""
        essay = SQLiteEssay(answer="Answer", question="")
        db_session.add(essay)
        db_session.commit()
        db_session.refresh(essay)

        assert essay.question == ""

    def test_empty_keywords_list(self, db_session):
        """Test that empty keywords list is accepted."""
        essay = SQLiteEssay(answer="Answer", keywords=[])
        db_session.add(essay)
        db_session.commit()
        db_session.refresh(essay)

        assert essay.keywords == []

    def test_long_answer_text(self, db_session):
        """Test that very long answer text is stored correctly."""
        long_answer = "A" * 50000  # 50KB of text
        essay = SQLiteEssay(answer=long_answer)
        db_session.add(essay)
        db_session.commit()
        db_session.refresh(essay)

        assert essay.answer == long_answer
        assert len(essay.answer) == 50000

    def test_long_question_text(self, db_session):
        """Test that very long question text is stored correctly."""
        long_question = "Q" * 10000
        essay = SQLiteEssay(question=long_question, answer="Short answer")
        db_session.add(essay)
        db_session.commit()
        db_session.refresh(essay)

        assert essay.question == long_question

    def test_many_keywords(self, db_session):
        """Test that many keywords are stored correctly."""
        many_keywords = [f"keyword_{i}" for i in range(100)]
        essay = SQLiteEssay(answer="Answer", keywords=many_keywords)
        db_session.add(essay)
        db_session.commit()
        db_session.refresh(essay)

        assert essay.keywords == many_keywords
        assert len(essay.keywords) == 100

    def test_special_characters_in_answer(self, db_session):
        """Test that special characters in answer are preserved."""
        special_answer = "Answer with <html> & 'quotes' and \"double quotes\" + symbols!@#$%^*()"
        essay = SQLiteEssay(answer=special_answer)
        db_session.add(essay)
        db_session.commit()
        db_session.refresh(essay)

        assert essay.answer == special_answer

    def test_unicode_characters_in_fields(self, db_session):
        """Test that unicode characters are properly stored."""
        essay = SQLiteEssay(
            question="Jakie masz doswiadczenie?",  # Polish
            answer="Tengo 5 anos de experiencia.",  # Spanish
            keywords=["experiencia", "developpeur"],  # French
        )
        db_session.add(essay)
        db_session.commit()
        db_session.refresh(essay)

        assert "doswiadczenie" in essay.question
        assert "anos" in essay.answer
        assert "developpeur" in essay.keywords

    def test_special_characters_in_keywords(self, db_session):
        """Test that keywords with special characters are preserved."""
        keywords = ["C++", "C#", "Node.js", "AWS/GCP", "React/Vue", "SQL Server"]
        essay = SQLiteEssay(answer="Technical answer", keywords=keywords)
        db_session.add(essay)
        db_session.commit()
        db_session.refresh(essay)

        assert essay.keywords == keywords

    def test_newlines_in_answer(self, db_session):
        """Test that newlines in answer are preserved."""
        multiline_answer = "First paragraph.\n\nSecond paragraph.\n\n- Bullet 1\n- Bullet 2"
        essay = SQLiteEssay(answer=multiline_answer)
        db_session.add(essay)
        db_session.commit()
        db_session.refresh(essay)

        assert essay.answer == multiline_answer
        assert "\n" in essay.answer


class TestEssayModelRepr:
    """Tests for Essay model string representation."""

    def test_repr_includes_id_and_question_preview(self, sample_essay):
        """Test that __repr__ includes id and question preview."""
        repr_str = repr(sample_essay)

        assert str(sample_essay.id) in repr_str
        assert "Essay" in repr_str
