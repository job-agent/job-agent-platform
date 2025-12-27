"""Shared test fixtures for essay-repository tests."""

from datetime import datetime, UTC
from typing import Generator
import json

import pytest
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy.types import TypeDecorator

from essay_repository.models.base import Base
from essay_repository.models import Essay  # noqa: F401 - Import to register with Base.metadata


class JSONArray(TypeDecorator):
    """Custom type that stores arrays as JSON in SQLite.

    PostgreSQL ARRAY type is not supported by SQLite, so we use this
    custom type to serialize/deserialize arrays as JSON strings.
    """

    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Convert list to JSON string for storage."""
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        """Convert JSON string back to list."""
        if value is not None:
            return json.loads(value)
        return value


# Create a test-specific Base for SQLite compatibility (used only in model tests)
class SQLiteTestBase(DeclarativeBase):
    """Base class for SQLite-compatible test models."""

    pass


class SQLiteEssay(SQLiteTestBase):
    """SQLite-compatible Essay model for testing.

    This model mirrors the production Essay model but uses JSONArray
    instead of PostgreSQL ARRAY for SQLite compatibility in tests.
    Used primarily for model-level tests that don't involve the repository.

    NOTE: Uses a different table name to avoid conflicts with the production
    Essay model when both are created in the same in-memory database.
    """

    __tablename__ = "test_essays"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question = Column(Text, nullable=True)
    answer = Column(Text, nullable=False)
    keywords = Column(JSONArray, nullable=True)
    embedding = Column(JSONArray, nullable=True)
    search_vector = Column(String, nullable=True)  # TSVECTOR stored as String in SQLite
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __repr__(self) -> str:
        """String representation of Essay."""
        question_preview = (
            self.question[:30] + "..."
            if self.question and len(self.question) > 30
            else self.question
        )
        return f"<Essay(id={self.id}, question='{question_preview}')>"


@pytest.fixture
def in_memory_engine():
    """Create an in-memory SQLite engine for testing.

    This fixture modifies the production Essay model's metadata to:
    1. Remove the PostgreSQL schema (essays) for SQLite compatibility
    2. Convert ARRAY columns to JSONArray for SQLite storage
    """
    engine = create_engine(
        "sqlite:///:memory:", echo=False, connect_args={"check_same_thread": False}
    )

    # Modify production model's metadata for SQLite compatibility
    # This follows the same pattern as jobs-repository
    for table in Base.metadata.tables.values():
        table.schema = None  # Remove schema for SQLite
        for column in table.columns:
            if hasattr(column.type, "__class__"):
                type_name = column.type.__class__.__name__
                if type_name == "ARRAY":
                    column.type = JSONArray()  # Convert ARRAY to JSONArray
                elif type_name == "TSVECTOR":
                    column.type = String()  # Convert TSVECTOR to String for SQLite

    # Also set up SQLiteTestBase for model-level tests
    SQLiteTestBase.metadata.create_all(engine)

    # Create production model tables
    Base.metadata.create_all(engine)

    yield engine
    engine.dispose()


@pytest.fixture
def db_session(in_memory_engine) -> Generator[Session, None, None]:
    """Create a database session for testing."""
    SessionLocal = sessionmaker(bind=in_memory_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def sample_essay(db_session) -> SQLiteEssay:
    """Create a sample essay for testing using SQLiteEssay model.

    Used primarily for model-level tests. For repository integration tests,
    use repo_sample_essay instead.
    """
    essay = SQLiteEssay(
        question="What is your greatest professional achievement?",
        answer="My greatest achievement was leading a team that delivered a critical project ahead of schedule.",
        keywords=["leadership", "project management", "teamwork"],
    )
    db_session.add(essay)
    db_session.commit()
    db_session.refresh(essay)
    return essay


@pytest.fixture
def sample_essay_create_dict():
    """Sample EssayCreate data for testing repository."""
    return {
        "question": "Why do you want to work at our company?",
        "answer": "I am passionate about the mission and believe my skills align perfectly with the role.",
        "keywords": ["motivation", "company culture", "career goals"],
    }


@pytest.fixture
def sample_essay_minimal_dict():
    """Sample minimal EssayCreate data with only required fields."""
    return {
        "answer": "This is a standalone answer without a question.",
    }


@pytest.fixture
def sample_essay_update_dict():
    """Sample EssayUpdate data for testing updates."""
    return {
        "answer": "Updated answer content.",
        "keywords": ["updated", "modified"],
    }


@pytest.fixture
def repo_sample_essay(db_session):
    """Create a sample essay using the repository for integration tests.

    This fixture creates essays through EssayRepository, which ensures
    the data is created using the production Essay model and can be
    properly retrieved by repository methods.
    """
    from essay_repository.repository import EssayRepository

    repository = EssayRepository(session=db_session)
    essay = repository.create(
        {
            "question": "What is your greatest professional achievement?",
            "answer": "My greatest achievement was leading a team.",
            "keywords": ["leadership", "project management", "teamwork"],
        }
    )
    return essay
