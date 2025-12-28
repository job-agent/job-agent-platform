"""Tests for EssaySearchService keyword generation integration.

These tests verify that EssaySearchService triggers keyword generation
on essay creation and does NOT trigger it on essay updates.
"""

import threading
from unittest.mock import MagicMock, patch


from job_agent_backend.services.essay_search_service import EssaySearchService


def _create_mock_repository() -> MagicMock:
    """Create a mock essay repository with basic functionality."""
    mock_repository = MagicMock()
    mock_repository.create.return_value = MagicMock(
        id=1,
        question="Test question?",
        answer="Test answer.",
        keywords=None,
    )
    mock_repository.update.return_value = MagicMock(
        id=1,
        question="Updated question?",
        answer="Updated answer.",
        keywords=["existing"],
    )
    mock_repository.update_embedding.return_value = True
    return mock_repository


def _create_mock_model_factory() -> MagicMock:
    """Create a mock model factory for embedding generation."""
    mock_factory = MagicMock()
    mock_model = MagicMock()
    mock_model.embed_query.return_value = [0.1] * 1536
    mock_factory.get_model.return_value = mock_model
    return mock_factory


def _create_mock_keyword_generator() -> MagicMock:
    """Create a mock keyword generator."""
    mock_generator = MagicMock()
    mock_generator.generate_keywords.return_value = ["Python", "leadership"]
    return mock_generator


class TestEssaySearchServiceCreateTriggersKeywordGeneration:
    """Tests for keyword generation trigger on create()."""

    def test_create_spawns_background_keyword_generation(self):
        """Service create() spawns a background thread for keyword generation."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        essay_data = {
            "question": "What is your experience?",
            "answer": "I have Python experience.",
        }

        with patch.object(threading, "Thread") as mock_thread_class:
            mock_thread = MagicMock()
            mock_thread_class.return_value = mock_thread

            service.create(essay_data)

            # Verify thread was created and started
            mock_thread_class.assert_called_once()
            mock_thread.start.assert_called_once()

    def test_create_passes_essay_data_to_keyword_generator(self):
        """Service create() passes essay ID, question, and answer to generator."""
        mock_repository = _create_mock_repository()
        created_essay = MagicMock(
            id=42,
            question="What are your skills?",
            answer="I know Python and Django.",
            keywords=None,
        )
        mock_repository.create.return_value = created_essay

        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        essay_data = {
            "question": "What are your skills?",
            "answer": "I know Python and Django.",
        }

        # Run without actually spawning a thread
        with patch.object(service, "_spawn_keyword_generation") as mock_spawn:
            service.create(essay_data)

            mock_spawn.assert_called_once_with(
                42,
                "What are your skills?",
                "I know Python and Django.",
            )

    def test_create_returns_immediately_without_waiting_for_keywords(self):
        """Service create() returns the essay without waiting for keyword generation."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        essay_data = {"answer": "Test answer"}

        with patch.object(threading, "Thread") as mock_thread_class:
            mock_thread = MagicMock()
            mock_thread_class.return_value = mock_thread

            result = service.create(essay_data)

            # Essay should be returned, and it should have keywords=None
            # (since keywords are generated async)
            assert result is not None
            assert result.keywords is None

    def test_create_spawns_daemon_thread(self):
        """Service create() spawns a daemon thread so it doesn't block shutdown."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        essay_data = {"answer": "Test answer"}

        with patch.object(threading, "Thread") as mock_thread_class:
            mock_thread = MagicMock()
            mock_thread_class.return_value = mock_thread

            service.create(essay_data)

            # Verify daemon=True was passed
            call_kwargs = mock_thread_class.call_args.kwargs
            assert call_kwargs.get("daemon") is True


class TestEssaySearchServiceUpdateDoesNotTriggerKeywordGeneration:
    """Tests verifying update() does NOT trigger keyword generation."""

    def test_update_does_not_spawn_keyword_generation(self):
        """Service update() does NOT spawn background keyword generation."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        essay_update = {"answer": "Updated answer"}

        with patch.object(service, "_spawn_keyword_generation") as mock_spawn:
            service.update(1, essay_update)

            mock_spawn.assert_not_called()

    def test_update_does_not_call_keyword_generator(self):
        """Service update() does NOT call the keyword generator."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        essay_update = {"answer": "Updated answer"}

        service.update(1, essay_update)

        mock_keyword_generator.generate_keywords.assert_not_called()

    def test_update_still_regenerates_embedding(self):
        """Service update() still regenerates embeddings (existing behavior)."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        essay_update = {"answer": "Updated answer"}

        service.update(1, essay_update)

        # Verify embedding is still generated
        mock_factory.get_model.assert_called_with(model_id="embedding")
        mock_repository.update_embedding.assert_called_once()


class TestEssaySearchServiceKeywordGeneratorInjection:
    """Tests for KeywordGenerator dependency injection."""

    def test_accepts_keyword_generator_in_constructor(self):
        """Service constructor accepts keyword_generator parameter."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        # Should not raise
        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        assert service is not None

class TestEssaySearchServiceBackgroundKeywordGenerationBehavior:
    """Tests for the background keyword generation behavior."""

    def test_background_thread_calls_keyword_generator(self):
        """Background thread invokes keyword generator with correct arguments."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        # Call the private method directly to test behavior
        service._generate_keywords_background(
            essay_id=42,
            question="What is your experience?",
            answer="I have Python experience.",
        )

        mock_keyword_generator.generate_keywords.assert_called_once_with(
            essay_id=42,
            question="What is your experience?",
            answer="I have Python experience.",
        )

    def test_background_method_handles_generator_exception(self):
        """Background method catches and logs generator exceptions."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = MagicMock()
        mock_keyword_generator.generate_keywords.side_effect = Exception("Generator error")

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        # Should not raise
        service._generate_keywords_background(
            essay_id=1,
            question="Question",
            answer="Answer",
        )

