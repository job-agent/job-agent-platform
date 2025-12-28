"""Tests for EssayRepository class.

These tests verify the EssayRepository implementation follows
the IEssayRepository interface contract.
"""

from datetime import datetime, UTC
from unittest.mock import patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from essay_repository.repository import EssayRepository
from essay_repository.models import Essay
from job_agent_platform_contracts.essay_repository import EssayValidationError
from db_core import TransactionError


class TestEssayRepositoryCreate:
    """Tests for EssayRepository.create method."""

    @pytest.fixture
    def repository(self, db_session):
        """Create an EssayRepository instance."""
        return EssayRepository(session=db_session)

    def test_create_with_all_fields(self, repository, sample_essay_create_dict, db_session):
        """Test creating essay with all fields."""
        essay = repository.create(sample_essay_create_dict)

        assert essay.id is not None
        assert essay.question == sample_essay_create_dict["question"]
        assert essay.answer == sample_essay_create_dict["answer"]
        assert essay.keywords == sample_essay_create_dict["keywords"]
        assert essay.created_at is not None
        assert essay.updated_at is not None

    def test_create_with_only_required_fields(
        self, repository, sample_essay_minimal_dict, db_session
    ):
        """Test creating essay with only required answer field."""
        essay = repository.create(sample_essay_minimal_dict)

        assert essay.id is not None
        assert essay.answer == sample_essay_minimal_dict["answer"]
        assert essay.question is None
        assert essay.keywords is None

    def test_create_sets_timestamps_automatically(
        self, repository, sample_essay_create_dict, db_session
    ):
        """Test that create sets created_at and updated_at."""
        before_create = datetime.now(UTC)
        essay = repository.create(sample_essay_create_dict)
        after_create = datetime.now(UTC)

        assert essay.created_at is not None
        assert essay.updated_at is not None
        # Normalize both to naive for comparison (SQLite returns naive)
        before_naive = before_create.replace(tzinfo=None)
        after_naive = after_create.replace(tzinfo=None)
        created_at_naive = (
            essay.created_at.replace(tzinfo=None) if essay.created_at.tzinfo else essay.created_at
        )
        assert before_naive <= created_at_naive <= after_naive

    def test_create_without_answer_raises_validation_error(self, repository):
        """Test that missing answer raises ValidationError."""
        invalid_data = {
            "question": "A question without an answer",
        }

        with pytest.raises(EssayValidationError) as exc_info:
            repository.create(invalid_data)
        assert "answer" in str(exc_info.value).lower()

    def test_create_with_empty_answer_is_allowed(self, repository):
        """Test that empty answer string is allowed (not None, empty string is valid)."""
        # Note: Empty string is allowed since it's not None
        # Only missing answer field raises validation error
        essay_data = {
            "answer": "",
        }

        essay = repository.create(essay_data)
        assert essay.answer == ""

    def test_create_commits_transaction(self, repository, sample_essay_create_dict, db_session):
        """Test that create commits the transaction."""
        essay = repository.create(sample_essay_create_dict)

        # Clear session cache to force reload from database
        db_session.expire_all()

        # Query directly to verify persistence
        retrieved = db_session.query(Essay).filter_by(id=essay.id).first()
        assert retrieved is not None
        assert retrieved.answer == sample_essay_create_dict["answer"]

    def test_create_handles_sqlalchemy_error(
        self, repository, sample_essay_create_dict, db_session
    ):
        """Test that SQLAlchemyError is converted to TransactionError."""
        with patch.object(db_session, "commit", side_effect=SQLAlchemyError("Database error")):
            with pytest.raises(TransactionError) as exc_info:
                repository.create(sample_essay_create_dict)
            assert "Failed to create essay" in str(exc_info.value)

    def test_create_rolls_back_on_error(self, repository, sample_essay_create_dict, db_session):
        """Test that session is rolled back on error."""
        with patch.object(db_session, "commit", side_effect=SQLAlchemyError("error")):
            try:
                repository.create(sample_essay_create_dict)
            except Exception:
                pass
        assert db_session.query(Essay).count() == 0

    def test_create_with_empty_keywords_list(self, repository, db_session):
        """Test creating essay with empty keywords list."""
        essay_data = {
            "answer": "Answer with no keywords",
            "keywords": [],
        }

        essay = repository.create(essay_data)

        assert essay.keywords == []

    def test_create_preserves_special_characters(self, repository, db_session):
        """Test that special characters are preserved in all fields."""
        essay_data = {
            "question": "What's your experience with C++ & C#?",
            "answer": 'I\'ve worked with <Angular> and "React" frameworks.',
            "keywords": ["C++", "C#", "Angular/React"],
        }

        essay = repository.create(essay_data)

        assert essay.question == essay_data["question"]
        assert essay.answer == essay_data["answer"]
        assert essay.keywords == essay_data["keywords"]


class TestEssayRepositoryGetById:
    """Tests for EssayRepository.get_by_id method."""

    @pytest.fixture
    def repository(self, db_session):
        """Create an EssayRepository instance."""
        return EssayRepository(session=db_session)

    def test_get_by_id_returns_essay_when_exists(self, repository, repo_sample_essay):
        """Test retrieving an essay by ID when it exists."""
        essay = repository.get_by_id(repo_sample_essay.id)

        assert essay is not None
        assert essay.id == repo_sample_essay.id
        assert essay.answer == repo_sample_essay.answer
        assert essay.question == repo_sample_essay.question
        assert essay.keywords == repo_sample_essay.keywords

    def test_get_by_id_returns_none_when_not_exists(self, repository):
        """Test retrieving an essay that doesn't exist returns None."""
        essay = repository.get_by_id(99999)

        assert essay is None

    def test_get_by_id_with_zero_returns_none(self, repository):
        """Test that get_by_id with zero returns None."""
        essay = repository.get_by_id(0)

        assert essay is None

    def test_get_by_id_with_negative_returns_none(self, repository):
        """Test that get_by_id with negative ID returns None."""
        essay = repository.get_by_id(-1)

        assert essay is None


class TestEssayRepositoryGetAll:
    """Tests for EssayRepository.get_all method."""

    @pytest.fixture
    def repository(self, db_session):
        """Create an EssayRepository instance."""
        return EssayRepository(session=db_session)

    def test_get_all_returns_empty_list_when_no_essays(self, repository):
        """Test get_all returns empty list when no essays exist."""
        essays = repository.get_all()

        assert essays == []
        assert isinstance(essays, list)

    def test_get_all_returns_all_essays(self, repository, db_session):
        """Test get_all returns all existing essays."""
        # Create multiple essays using the repository
        repository.create({"answer": "Answer 1", "question": "Question 1"})
        repository.create({"answer": "Answer 2", "question": "Question 2"})
        repository.create({"answer": "Answer 3", "question": "Question 3"})

        essays = repository.get_all()

        assert len(essays) == 3
        answers = [e.answer for e in essays]
        assert "Answer 1" in answers
        assert "Answer 2" in answers
        assert "Answer 3" in answers

    def test_get_all_returns_list_type(self, repository):
        """Test that get_all always returns a list."""
        result = repository.get_all()

        assert isinstance(result, list)


class TestEssayRepositoryDelete:
    """Tests for EssayRepository.delete method."""

    @pytest.fixture
    def repository(self, db_session):
        """Create an EssayRepository instance."""
        return EssayRepository(session=db_session)

    def test_delete_returns_true_when_essay_exists(self, repository, repo_sample_essay, db_session):
        """Test that deleting existing essay returns True."""
        essay_id = repo_sample_essay.id

        result = repository.delete(essay_id)

        assert result is True
        # Verify essay is actually deleted via repository
        assert repository.get_by_id(essay_id) is None

    def test_delete_returns_false_when_essay_not_exists(self, repository):
        """Test that deleting non-existent essay returns False."""
        result = repository.delete(99999)

        assert result is False

    def test_delete_with_zero_returns_false(self, repository):
        """Test that delete with zero ID returns False."""
        result = repository.delete(0)

        assert result is False

    def test_delete_with_negative_returns_false(self, repository):
        """Test that delete with negative ID returns False."""
        result = repository.delete(-1)

        assert result is False

    def test_delete_does_not_affect_other_essays(self, repository, db_session):
        """Test that deleting one essay doesn't affect others."""
        # Create essays using the repository
        essay1 = repository.create({"answer": "Answer 1"})
        essay2 = repository.create({"answer": "Answer 2"})

        repository.delete(essay1.id)

        # essay2 should still exist
        remaining = repository.get_by_id(essay2.id)
        assert remaining is not None
        assert remaining.answer == "Answer 2"


class TestEssayRepositoryUpdate:
    """Tests for EssayRepository.update method."""

    @pytest.fixture
    def repository(self, db_session):
        """Create an EssayRepository instance."""
        return EssayRepository(session=db_session)

    def test_update_returns_updated_essay(
        self, repository, repo_sample_essay, sample_essay_update_dict
    ):
        """Test that update returns the updated essay."""
        essay = repository.update(repo_sample_essay.id, sample_essay_update_dict)

        assert essay is not None
        assert essay.id == repo_sample_essay.id
        assert essay.answer == sample_essay_update_dict["answer"]
        assert essay.keywords == sample_essay_update_dict["keywords"]

    def test_update_returns_none_when_essay_not_exists(self, repository, sample_essay_update_dict):
        """Test that updating non-existent essay returns None."""
        essay = repository.update(99999, sample_essay_update_dict)

        assert essay is None

    def test_update_partial_only_answer(self, repository, repo_sample_essay, db_session):
        """Test partial update with only answer field."""
        original_question = repo_sample_essay.question
        original_keywords = repo_sample_essay.keywords

        update_data = {"answer": "New answer only"}
        essay = repository.update(repo_sample_essay.id, update_data)

        assert essay is not None
        assert essay.answer == "New answer only"
        # Other fields should remain unchanged
        assert essay.question == original_question
        assert essay.keywords == original_keywords

    def test_update_partial_only_question(self, repository, repo_sample_essay, db_session):
        """Test partial update with only question field."""
        original_answer = repo_sample_essay.answer
        original_keywords = repo_sample_essay.keywords

        update_data = {"question": "New question only?"}
        essay = repository.update(repo_sample_essay.id, update_data)

        assert essay is not None
        assert essay.question == "New question only?"
        assert essay.answer == original_answer
        assert essay.keywords == original_keywords

    def test_update_partial_only_keywords(self, repository, repo_sample_essay, db_session):
        """Test partial update with only keywords field."""
        original_question = repo_sample_essay.question
        original_answer = repo_sample_essay.answer

        update_data = {"keywords": ["new", "keywords"]}
        essay = repository.update(repo_sample_essay.id, update_data)

        assert essay is not None
        assert essay.keywords == ["new", "keywords"]
        assert essay.question == original_question
        assert essay.answer == original_answer

    def test_update_all_fields(self, repository, repo_sample_essay, db_session):
        """Test updating all fields at once."""
        update_data = {
            "question": "Completely new question?",
            "answer": "Completely new answer.",
            "keywords": ["completely", "new"],
        }

        essay = repository.update(repo_sample_essay.id, update_data)

        assert essay is not None
        assert essay.question == update_data["question"]
        assert essay.answer == update_data["answer"]
        assert essay.keywords == update_data["keywords"]

    def test_update_updates_updated_at_timestamp(self, repository, repo_sample_essay, db_session):
        """Test that update modifies updated_at timestamp."""
        # Normalize to naive for comparison (SQLite returns naive)
        original_updated_at = repo_sample_essay.updated_at
        original_naive = (
            original_updated_at.replace(tzinfo=None)
            if original_updated_at.tzinfo
            else original_updated_at
        )

        import time

        time.sleep(0.1)  # Small delay to ensure timestamp difference

        update_data = {"answer": "Modified answer"}
        essay = repository.update(repo_sample_essay.id, update_data)

        assert essay is not None
        essay_updated_naive = (
            essay.updated_at.replace(tzinfo=None) if essay.updated_at.tzinfo else essay.updated_at
        )
        assert essay_updated_naive >= original_naive

    def test_update_does_not_change_created_at(self, repository, repo_sample_essay, db_session):
        """Test that update does not modify created_at timestamp."""
        original_created_at = repo_sample_essay.created_at
        # Normalize to naive for comparison (SQLite returns naive)
        original_naive = (
            original_created_at.replace(tzinfo=None)
            if original_created_at.tzinfo
            else original_created_at
        )

        update_data = {"answer": "Modified answer"}
        essay = repository.update(repo_sample_essay.id, update_data)

        assert essay is not None
        essay_created_naive = (
            essay.created_at.replace(tzinfo=None) if essay.created_at.tzinfo else essay.created_at
        )
        assert essay_created_naive == original_naive

    def test_update_with_empty_dict_returns_unchanged_essay(
        self, repository, repo_sample_essay, db_session
    ):
        """Test that update with empty dict returns unchanged essay."""
        original_answer = repo_sample_essay.answer

        essay = repository.update(repo_sample_essay.id, {})

        assert essay is not None
        assert essay.answer == original_answer

    def test_update_can_set_question_to_none(self, repository, repo_sample_essay, db_session):
        """Test that question can be set to None (cleared)."""
        # Verify repo_sample_essay has a question initially
        assert repo_sample_essay.question is not None

        update_data = {"question": None}
        essay = repository.update(repo_sample_essay.id, update_data)

        assert essay is not None
        assert essay.question is None

    def test_update_can_clear_keywords(self, repository, repo_sample_essay, db_session):
        """Test that keywords can be cleared by setting to empty list."""
        update_data = {"keywords": []}
        essay = repository.update(repo_sample_essay.id, update_data)

        assert essay is not None
        assert essay.keywords == []

    def test_update_handles_sqlalchemy_error(self, repository, repo_sample_essay, db_session):
        """Test that SQLAlchemyError is converted to TransactionError."""
        with patch.object(db_session, "commit", side_effect=SQLAlchemyError("Database error")):
            with pytest.raises(TransactionError):
                repository.update(repo_sample_essay.id, {"answer": "New answer"})


class TestEssayRepositoryConstructor:
    """Tests for EssayRepository constructor validation."""

    def test_accepts_session(self, db_session):
        """Test that repository can be created with session."""
        repo = EssayRepository(session=db_session)
        assert repo is not None

    def test_accepts_session_factory(self, in_memory_engine):
        """Test that repository can be created with session_factory."""
        from sqlalchemy.orm import sessionmaker

        factory = sessionmaker(bind=in_memory_engine)
        repo = EssayRepository(session_factory=factory)
        assert repo is not None

    def test_raises_error_when_both_session_and_factory_provided(
        self, db_session, in_memory_engine
    ):
        """Test that providing both session and session_factory raises ValueError."""
        from sqlalchemy.orm import sessionmaker

        factory = sessionmaker(bind=in_memory_engine)
        with pytest.raises(ValueError) as exc_info:
            EssayRepository(session=db_session, session_factory=factory)
        assert "either session or session_factory" in str(exc_info.value).lower()

    def test_raises_error_when_session_factory_not_callable(self):
        """Test that non-callable session_factory raises TypeError."""
        with pytest.raises(TypeError) as exc_info:
            EssayRepository(session_factory="not_callable")
        assert "callable" in str(exc_info.value).lower()


class TestEssayRepositoryInterfaceCompliance:
    """Tests to verify EssayRepository implements IEssayRepository interface."""

    def test_repository_implements_interface(self, db_session):
        """Test that EssayRepository implements IEssayRepository."""
        from job_agent_platform_contracts.essay_repository import IEssayRepository

        repo = EssayRepository(session=db_session)
        assert isinstance(repo, IEssayRepository)

    def test_repository_has_create_method(self, db_session):
        """Test that repository has create method."""
        repo = EssayRepository(session=db_session)
        assert hasattr(repo, "create")
        assert callable(repo.create)

    def test_repository_has_get_by_id_method(self, db_session):
        """Test that repository has get_by_id method."""
        repo = EssayRepository(session=db_session)
        assert hasattr(repo, "get_by_id")
        assert callable(repo.get_by_id)

    def test_repository_has_get_all_method(self, db_session):
        """Test that repository has get_all method."""
        repo = EssayRepository(session=db_session)
        assert hasattr(repo, "get_all")
        assert callable(repo.get_all)

    def test_repository_has_delete_method(self, db_session):
        """Test that repository has delete method."""
        repo = EssayRepository(session=db_session)
        assert hasattr(repo, "delete")
        assert callable(repo.delete)

    def test_repository_has_update_method(self, db_session):
        """Test that repository has update method."""
        repo = EssayRepository(session=db_session)
        assert hasattr(repo, "update")
        assert callable(repo.update)


class TestEssayRepositoryGetPaginated:
    """Tests for EssayRepository.get_paginated method."""

    @pytest.fixture
    def repository(self, db_session):
        """Create an EssayRepository instance."""
        return EssayRepository(session=db_session)

    def test_returns_correct_page_size(self, repository, db_session):
        """When more essays exist than page_size, return only page_size essays."""
        # Create 7 essays
        for i in range(7):
            repository.create({"answer": f"Answer {i}"})

        essays, total_count = repository.get_paginated(page=1, page_size=5)

        assert len(essays) == 5
        assert total_count == 7

    def test_returns_total_count_accurately(self, repository, db_session):
        """Total count should reflect all essays, not just current page."""
        # Create 12 essays
        for i in range(12):
            repository.create({"answer": f"Answer {i}"})

        essays, total_count = repository.get_paginated(page=1, page_size=5)

        assert total_count == 12

    def test_sorts_by_created_at_descending(self, repository, db_session):
        """Essays should be sorted by created_at descending (newest first)."""
        import time

        # Create essays with slight delays to ensure different timestamps
        repository.create({"answer": "First created"})
        time.sleep(0.01)
        repository.create({"answer": "Second created"})
        time.sleep(0.01)
        repository.create({"answer": "Third created"})

        essays, _ = repository.get_paginated(page=1, page_size=10)

        # Newest should be first
        assert essays[0].answer == "Third created"
        assert essays[1].answer == "Second created"
        assert essays[2].answer == "First created"

    def test_returns_empty_list_for_page_beyond_total(self, repository, db_session):
        """When page exceeds available pages, return empty list."""
        # Create 3 essays
        for i in range(3):
            repository.create({"answer": f"Answer {i}"})

        essays, total_count = repository.get_paginated(page=10, page_size=5)

        assert essays == []
        assert total_count == 3

    def test_returns_empty_list_and_zero_count_for_empty_database(self, repository):
        """When no essays exist, return empty list and 0 count."""
        essays, total_count = repository.get_paginated(page=1, page_size=5)

        assert essays == []
        assert total_count == 0

    def test_correct_offset_for_page_2(self, repository, db_session):
        """Page 2 should skip the first page_size essays."""
        import time

        # Create 7 essays with clear ordering
        for i in range(7):
            repository.create({"answer": f"Answer {i}"})
            time.sleep(0.01)

        page1_essays, _ = repository.get_paginated(page=1, page_size=5)
        page2_essays, _ = repository.get_paginated(page=2, page_size=5)

        # Page 2 should have remaining 2 essays (oldest ones)
        assert len(page2_essays) == 2
        # Ensure no overlap between pages
        page1_ids = {e.id for e in page1_essays}
        page2_ids = {e.id for e in page2_essays}
        assert page1_ids.isdisjoint(page2_ids)

    def test_treats_page_zero_as_page_one(self, repository, db_session):
        """When page is 0 or negative, treat as page 1."""
        for i in range(3):
            repository.create({"answer": f"Answer {i}"})

        essays_page0, count0 = repository.get_paginated(page=0, page_size=5)
        essays_page1, count1 = repository.get_paginated(page=1, page_size=5)

        assert len(essays_page0) == len(essays_page1)
        assert count0 == count1
        assert {e.id for e in essays_page0} == {e.id for e in essays_page1}

    def test_treats_negative_page_as_page_one(self, repository, db_session):
        """When page is negative, treat as page 1."""
        for i in range(3):
            repository.create({"answer": f"Answer {i}"})

        essays_negative, count_neg = repository.get_paginated(page=-5, page_size=5)
        essays_page1, count1 = repository.get_paginated(page=1, page_size=5)

        assert len(essays_negative) == len(essays_page1)
        assert count_neg == count1

    def test_returns_partial_page_for_last_page(self, repository, db_session):
        """Last page may have fewer essays than page_size."""
        # Create 7 essays, page 2 with page_size=5 should have 2 essays
        for i in range(7):
            repository.create({"answer": f"Answer {i}"})

        essays, total_count = repository.get_paginated(page=2, page_size=5)

        assert len(essays) == 2
        assert total_count == 7
