"""Tests for Essay schemas from job-agent-platform-contracts.

These tests verify the EssayCreate, EssayUpdate, and Essay schemas
are correctly defined and can be used for validation.
"""

import pytest
from datetime import datetime, UTC

from job_agent_platform_contracts.essay_repository.schemas import (
    EssayCreate,
    EssayUpdate,
    Essay,
)


class TestEssayCreateSchema:
    """Tests for EssayCreate TypedDict schema."""

    def test_essay_create_accepts_all_fields(self):
        """Test that EssayCreate accepts all defined fields."""
        essay_data: EssayCreate = {
            "question": "What is your experience?",
            "answer": "I have 5 years of experience.",
            "keywords": ["experience", "background"],
        }

        assert essay_data["question"] == "What is your experience?"
        assert essay_data["answer"] == "I have 5 years of experience."
        assert essay_data["keywords"] == ["experience", "background"]

    def test_essay_create_accepts_only_answer(self):
        """Test that EssayCreate works with only the required answer field."""
        essay_data: EssayCreate = {
            "answer": "My answer without a question.",
        }

        assert essay_data["answer"] == "My answer without a question."
        assert "question" not in essay_data
        assert "keywords" not in essay_data

    def test_essay_create_accepts_answer_and_question(self):
        """Test that EssayCreate works with answer and question."""
        essay_data: EssayCreate = {
            "question": "Why should we hire you?",
            "answer": "Because I am qualified.",
        }

        assert essay_data["question"] == "Why should we hire you?"
        assert essay_data["answer"] == "Because I am qualified."
        assert "keywords" not in essay_data

    def test_essay_create_accepts_answer_and_keywords(self):
        """Test that EssayCreate works with answer and keywords."""
        essay_data: EssayCreate = {
            "answer": "My skills include Python and SQL.",
            "keywords": ["python", "sql", "skills"],
        }

        assert essay_data["answer"] == "My skills include Python and SQL."
        assert essay_data["keywords"] == ["python", "sql", "skills"]
        assert "question" not in essay_data

    def test_essay_create_keywords_can_be_empty_list(self):
        """Test that EssayCreate accepts empty keywords list."""
        essay_data: EssayCreate = {
            "answer": "An answer with no keywords.",
            "keywords": [],
        }

        assert essay_data["keywords"] == []

    def test_essay_create_answer_can_be_long_text(self):
        """Test that EssayCreate accepts long answer text."""
        long_answer = "This is a very long answer. " * 1000
        essay_data: EssayCreate = {
            "answer": long_answer,
        }

        assert essay_data["answer"] == long_answer
        assert len(essay_data["answer"]) > 10000


class TestEssayUpdateSchema:
    """Tests for EssayUpdate TypedDict schema."""

    def test_essay_update_accepts_all_fields(self):
        """Test that EssayUpdate accepts all defined fields."""
        update_data: EssayUpdate = {
            "question": "Updated question?",
            "answer": "Updated answer.",
            "keywords": ["updated", "modified"],
        }

        assert update_data["question"] == "Updated question?"
        assert update_data["answer"] == "Updated answer."
        assert update_data["keywords"] == ["updated", "modified"]

    def test_essay_update_accepts_only_question(self):
        """Test that EssayUpdate works with only question (partial update)."""
        update_data: EssayUpdate = {
            "question": "New question?",
        }

        assert update_data["question"] == "New question?"
        assert "answer" not in update_data
        assert "keywords" not in update_data

    def test_essay_update_accepts_only_answer(self):
        """Test that EssayUpdate works with only answer (partial update)."""
        update_data: EssayUpdate = {
            "answer": "New answer content.",
        }

        assert update_data["answer"] == "New answer content."
        assert "question" not in update_data
        assert "keywords" not in update_data

    def test_essay_update_accepts_only_keywords(self):
        """Test that EssayUpdate works with only keywords (partial update)."""
        update_data: EssayUpdate = {
            "keywords": ["new", "tags"],
        }

        assert update_data["keywords"] == ["new", "tags"]
        assert "question" not in update_data
        assert "answer" not in update_data

    def test_essay_update_can_be_empty(self):
        """Test that EssayUpdate can be empty (no fields to update)."""
        update_data: EssayUpdate = {}

        assert len(update_data) == 0

    def test_essay_update_keywords_can_be_empty_list(self):
        """Test that EssayUpdate accepts empty keywords list to clear keywords."""
        update_data: EssayUpdate = {
            "keywords": [],
        }

        assert update_data["keywords"] == []


class TestEssayResponseSchema:
    """Tests for Essay Pydantic response schema."""

    def test_essay_schema_requires_all_mandatory_fields(self):
        """Test that Essay schema requires id, answer, created_at, updated_at."""
        now = datetime.now(UTC)
        essay = Essay(
            id=1,
            answer="Required answer.",
            created_at=now,
            updated_at=now,
        )

        assert essay.id == 1
        assert essay.answer == "Required answer."
        assert essay.created_at == now
        assert essay.updated_at == now
        assert essay.question is None
        assert essay.keywords is None

    def test_essay_schema_accepts_all_fields(self):
        """Test that Essay schema accepts all fields including optionals."""
        now = datetime.now(UTC)
        essay = Essay(
            id=42,
            question="What is your experience?",
            answer="I have 5 years of experience.",
            keywords=["experience", "background"],
            created_at=now,
            updated_at=now,
        )

        assert essay.id == 42
        assert essay.question == "What is your experience?"
        assert essay.answer == "I have 5 years of experience."
        assert essay.keywords == ["experience", "background"]
        assert essay.created_at == now
        assert essay.updated_at == now

    def test_essay_schema_from_attributes_config(self):
        """Test that Essay schema has from_attributes=True for ORM compatibility."""
        assert Essay.model_config.get("from_attributes") is True

    def test_essay_schema_validates_id_is_integer(self):
        """Test that Essay schema validates id as integer."""
        now = datetime.now(UTC)
        with pytest.raises(Exception):  # Pydantic ValidationError
            Essay(
                id="not-an-int",
                answer="Answer",
                created_at=now,
                updated_at=now,
            )

    def test_essay_schema_validates_answer_is_required(self):
        """Test that Essay schema requires answer field."""
        now = datetime.now(UTC)
        with pytest.raises(Exception):  # Pydantic ValidationError
            Essay(
                id=1,
                created_at=now,
                updated_at=now,
            )

    def test_essay_schema_keywords_can_be_none(self):
        """Test that keywords can be explicitly None."""
        now = datetime.now(UTC)
        essay = Essay(
            id=1,
            answer="Answer",
            keywords=None,
            created_at=now,
            updated_at=now,
        )

        assert essay.keywords is None

    def test_essay_schema_keywords_can_be_empty_list(self):
        """Test that keywords can be an empty list."""
        now = datetime.now(UTC)
        essay = Essay(
            id=1,
            answer="Answer",
            keywords=[],
            created_at=now,
            updated_at=now,
        )

        assert essay.keywords == []
