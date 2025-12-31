"""Tests for EssaySearchService async operations.

These tests verify:
1. Keyword generation triggers on essay creation (existing behavior)
2. Keyword generation does NOT trigger on essay updates (existing behavior)
3. Embedding generation runs asynchronously in background threads
4. Background embedding handles failures gracefully
5. Essays are immediately searchable after creation (before embedding completes)
"""

import threading
from unittest.mock import MagicMock, patch

import pytest

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

        # Isolate keyword thread by patching embedding generation
        with patch.object(service, "_spawn_embedding_generation"):
            with patch.object(threading, "Thread") as mock_thread_class:
                mock_thread = MagicMock()
                mock_thread_class.return_value = mock_thread

                service.create(essay_data)

                # Verify thread was created and started for keyword generation
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


class TestEssaySearchServiceAsyncEmbeddingOnCreate:
    """Tests for async embedding generation on essay creation."""

    def test_create_spawns_background_embedding_generation(self):
        """Service create() spawns a background thread for embedding generation."""
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

        with patch.object(service, "_spawn_embedding_generation") as mock_spawn:
            service.create(essay_data)

            mock_spawn.assert_called_once()

    def test_create_passes_essay_data_to_embedding_generator(self):
        """Service create() passes essay ID and content to embedding generation."""
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

        with patch.object(service, "_spawn_embedding_generation") as mock_spawn:
            service.create(essay_data)

            mock_spawn.assert_called_once_with(
                essay_id=42,
                question="What are your skills?",
                answer="I know Python and Django.",
                keywords=None,
            )

    def test_create_returns_immediately_without_waiting_for_embedding(self):
        """Service create() returns essay without waiting for embedding generation."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        essay_data = {"answer": "Test answer"}

        with patch.object(service, "_spawn_embedding_generation"):
            result = service.create(essay_data)

            # Essay should be returned immediately
            assert result is not None
            # Repository update_embedding should NOT have been called synchronously
            mock_repository.update_embedding.assert_not_called()

    def test_create_spawns_embedding_thread_with_daemon_true(self):
        """Service create() spawns embedding thread as daemon."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        essay_data = {"answer": "Test answer"}

        # We need to patch Thread to capture the daemon parameter
        # The spawn method should create a Thread with daemon=True
        with patch.object(threading, "Thread") as mock_thread_class:
            mock_thread = MagicMock()
            mock_thread_class.return_value = mock_thread

            # Patch to isolate embedding thread from keyword thread
            with patch.object(service, "_spawn_keyword_generation"):
                service.create(essay_data)

            # Find the call for embedding generation (should have target containing
            # "embedding")
            embedding_call = None
            for call in mock_thread_class.call_args_list:
                if "embedding" in str(call.kwargs.get("target", "")):
                    embedding_call = call
                    break

            # Verify daemon=True was passed
            assert embedding_call is not None, "No embedding thread was spawned"
            assert embedding_call.kwargs.get("daemon") is True

    def test_create_persists_essay_before_spawning_embedding_thread(self):
        """Service create() persists essay to DB before spawning embedding thread."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        essay_data = {"answer": "Test answer"}

        call_order = []

        def track_create(*args, **kwargs):
            call_order.append("create")
            return MagicMock(id=1, question=None, answer="Test answer", keywords=None)

        def track_spawn(*args, **kwargs):
            call_order.append("spawn_embedding")

        mock_repository.create.side_effect = track_create

        with patch.object(service, "_spawn_embedding_generation", side_effect=track_spawn):
            with patch.object(service, "_spawn_keyword_generation"):
                service.create(essay_data)

        assert call_order == ["create", "spawn_embedding"]


class TestEssaySearchServiceAsyncEmbeddingOnUpdate:
    """Tests for async embedding generation on essay update."""

    def test_update_spawns_background_embedding_generation(self):
        """Service update() spawns a background thread for embedding regeneration."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        essay_update = {"answer": "Updated answer"}

        with patch.object(service, "_spawn_embedding_generation") as mock_spawn:
            service.update(1, essay_update)

            mock_spawn.assert_called_once()

    def test_update_passes_essay_data_to_embedding_generator(self):
        """Service update() passes essay ID and updated content to embedding generation."""
        mock_repository = _create_mock_repository()
        updated_essay = MagicMock(
            id=42,
            question="Updated question?",
            answer="Updated answer.",
            keywords=["existing", "keywords"],
        )
        mock_repository.update.return_value = updated_essay

        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        essay_update = {"answer": "Updated answer."}

        with patch.object(service, "_spawn_embedding_generation") as mock_spawn:
            service.update(42, essay_update)

            mock_spawn.assert_called_once_with(
                essay_id=42,
                question="Updated question?",
                answer="Updated answer.",
                keywords=["existing", "keywords"],
            )

    def test_update_returns_immediately_without_waiting_for_embedding(self):
        """Service update() returns essay without waiting for embedding regeneration."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        essay_update = {"answer": "Updated answer"}

        with patch.object(service, "_spawn_embedding_generation"):
            result = service.update(1, essay_update)

            # Essay should be returned immediately
            assert result is not None
            # Repository update_embedding should NOT have been called synchronously
            mock_repository.update_embedding.assert_not_called()

    def test_update_spawns_embedding_thread_with_daemon_true(self):
        """Service update() spawns embedding thread as daemon."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        essay_update = {"answer": "Updated answer"}

        with patch.object(threading, "Thread") as mock_thread_class:
            mock_thread = MagicMock()
            mock_thread_class.return_value = mock_thread

            service.update(1, essay_update)

            # Verify daemon=True was passed
            call_kwargs = mock_thread_class.call_args.kwargs
            assert call_kwargs.get("daemon") is True

    def test_update_does_not_spawn_embedding_when_essay_not_found(self):
        """Service update() does not spawn embedding thread when essay not found."""
        mock_repository = _create_mock_repository()
        mock_repository.update.return_value = None

        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        essay_update = {"answer": "Updated answer"}

        with patch.object(service, "_spawn_embedding_generation") as mock_spawn:
            result = service.update(999, essay_update)

            assert result is None
            mock_spawn.assert_not_called()


class TestEssaySearchServiceBackgroundEmbeddingGeneration:
    """Tests for the background embedding generation behavior."""

    def test_background_embedding_calls_model_factory(self):
        """Background embedding invokes model factory with 'embedding' model ID."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        service._generate_embedding_background(
            essay_id=42,
            question="What is your experience?",
            answer="I have Python experience.",
            keywords=["Python", "experience"],
        )

        mock_factory.get_model.assert_called_with(model_id="embedding")

    def test_background_embedding_generates_embedding_from_content(self):
        """Background embedding generates embedding from question, answer, and keywords."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_model = mock_factory.get_model.return_value
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        service._generate_embedding_background(
            essay_id=42,
            question="What is your experience?",
            answer="I have Python experience.",
            keywords=["Python", "experience"],
        )

        # Verify embed_query was called with combined text
        mock_model.embed_query.assert_called_once()
        call_args = mock_model.embed_query.call_args[0][0]
        assert "What is your experience?" in call_args
        assert "I have Python experience." in call_args
        assert "Python" in call_args

    def test_background_embedding_persists_to_repository(self):
        """Background embedding persists generated embedding to repository."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_model = mock_factory.get_model.return_value
        mock_model.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        service._generate_embedding_background(
            essay_id=42,
            question="Question",
            answer="Answer",
            keywords=None,
        )

        mock_repository.update_embedding.assert_called_once_with(42, [0.1, 0.2, 0.3])

    def test_background_embedding_handles_model_factory_exception(self):
        """Background embedding catches and logs model factory exceptions."""
        mock_repository = _create_mock_repository()
        mock_factory = MagicMock()
        mock_factory.get_model.side_effect = Exception("Model unavailable")
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        # Should not raise
        service._generate_embedding_background(
            essay_id=1,
            question="Question",
            answer="Answer",
            keywords=None,
        )

        # Repository should not be called if model fails
        mock_repository.update_embedding.assert_not_called()

    def test_background_embedding_handles_embed_query_exception(self):
        """Background embedding catches and logs embedding generation exceptions."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_model = mock_factory.get_model.return_value
        mock_model.embed_query.side_effect = Exception("Embedding generation failed")
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        # Should not raise
        service._generate_embedding_background(
            essay_id=1,
            question="Question",
            answer="Answer",
            keywords=None,
        )

        # Repository should not be called if embedding fails
        mock_repository.update_embedding.assert_not_called()

    def test_background_embedding_handles_repository_exception(self):
        """Background embedding catches and logs repository exceptions."""
        mock_repository = _create_mock_repository()
        mock_repository.update_embedding.side_effect = Exception("DB connection failed")
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        # Should not raise
        service._generate_embedding_background(
            essay_id=1,
            question="Question",
            answer="Answer",
            keywords=None,
        )

    def test_background_embedding_does_not_propagate_exception(self):
        """Background embedding does not propagate exceptions to caller."""
        mock_repository = _create_mock_repository()
        mock_factory = MagicMock()
        mock_factory.get_model.side_effect = RuntimeError("Unexpected error")
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        # Should not raise any exception
        service._generate_embedding_background(
            essay_id=1,
            question="Question",
            answer="Answer",
            keywords=None,
        )


class TestEssaySearchServiceSpawnEmbeddingGeneration:
    """Tests for the _spawn_embedding_generation method."""

    def test_spawn_creates_thread_with_correct_target(self):
        """Spawn method creates thread with _generate_embedding_background as target."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        with patch.object(threading, "Thread") as mock_thread_class:
            mock_thread = MagicMock()
            mock_thread_class.return_value = mock_thread

            service._spawn_embedding_generation(
                essay_id=42,
                question="Question",
                answer="Answer",
                keywords=["keyword"],
            )

            mock_thread_class.assert_called_once()
            call_kwargs = mock_thread_class.call_args.kwargs
            assert call_kwargs["target"] == service._generate_embedding_background

    def test_spawn_creates_thread_with_correct_args(self):
        """Spawn method creates thread with correct arguments."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        with patch.object(threading, "Thread") as mock_thread_class:
            mock_thread = MagicMock()
            mock_thread_class.return_value = mock_thread

            service._spawn_embedding_generation(
                essay_id=42,
                question="Test question",
                answer="Test answer",
                keywords=["Python", "Django"],
            )

            call_kwargs = mock_thread_class.call_args.kwargs
            assert call_kwargs["args"] == (42, "Test question", "Test answer", ["Python", "Django"])

    def test_spawn_creates_daemon_thread(self):
        """Spawn method creates daemon thread that does not block shutdown."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        with patch.object(threading, "Thread") as mock_thread_class:
            mock_thread = MagicMock()
            mock_thread_class.return_value = mock_thread

            service._spawn_embedding_generation(
                essay_id=42,
                question="Question",
                answer="Answer",
                keywords=None,
            )

            call_kwargs = mock_thread_class.call_args.kwargs
            assert call_kwargs["daemon"] is True

    def test_spawn_starts_the_thread(self):
        """Spawn method starts the created thread."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        with patch.object(threading, "Thread") as mock_thread_class:
            mock_thread = MagicMock()
            mock_thread_class.return_value = mock_thread

            service._spawn_embedding_generation(
                essay_id=42,
                question="Question",
                answer="Answer",
                keywords=None,
            )

            mock_thread.start.assert_called_once()


class TestEssaySearchServiceImmediateSearchability:
    """Tests verifying essays are immediately searchable after creation."""

    def test_essay_persisted_with_null_embedding_initially(self):
        """Essay is persisted to database before embedding generation starts."""
        mock_repository = _create_mock_repository()
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        essay_data = {"question": "Question", "answer": "Answer"}

        with patch.object(service, "_spawn_embedding_generation"):
            with patch.object(service, "_spawn_keyword_generation"):
                service.create(essay_data)

        # Repository create was called
        mock_repository.create.assert_called_once_with(essay_data)
        # But update_embedding was NOT called synchronously
        mock_repository.update_embedding.assert_not_called()

    def test_create_returns_essay_with_null_embedding(self):
        """Create returns essay object immediately with embedding field unset."""
        mock_repository = _create_mock_repository()
        created_essay = MagicMock(
            id=1,
            question="Test question?",
            answer="Test answer.",
            keywords=None,
            embedding=None,
        )
        mock_repository.create.return_value = created_essay

        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        essay_data = {"question": "Test question?", "answer": "Test answer."}

        with patch.object(service, "_spawn_embedding_generation"):
            with patch.object(service, "_spawn_keyword_generation"):
                result = service.create(essay_data)

        # Essay is returned with embedding=None
        assert result.embedding is None
        assert result.question == "Test question?"
        assert result.answer == "Test answer."


class TestEssaySearchServiceDelete:
    """Tests for EssaySearchService.delete method."""

    def test_delete_delegates_to_repository(self):
        """Service delete() calls repository.delete() with the essay ID."""
        mock_repository = _create_mock_repository()
        mock_repository.delete.return_value = True
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        service.delete(42)

        mock_repository.delete.assert_called_once_with(42)

    def test_delete_returns_true_when_essay_exists(self):
        """Service delete() returns True when repository successfully deletes essay."""
        mock_repository = _create_mock_repository()
        mock_repository.delete.return_value = True
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        result = service.delete(42)

        assert result is True

    def test_delete_returns_false_when_essay_not_exists(self):
        """Service delete() returns False when essay does not exist."""
        mock_repository = _create_mock_repository()
        mock_repository.delete.return_value = False
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        result = service.delete(99999)

        assert result is False

    def test_delete_with_zero_id_returns_false(self):
        """Service delete() with zero ID returns False."""
        mock_repository = _create_mock_repository()
        mock_repository.delete.return_value = False
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        result = service.delete(0)

        assert result is False

    def test_delete_with_negative_id_returns_false(self):
        """Service delete() with negative ID returns False."""
        mock_repository = _create_mock_repository()
        mock_repository.delete.return_value = False
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        result = service.delete(-1)

        assert result is False

    def test_delete_propagates_repository_exception(self):
        """Service delete() propagates exceptions from repository."""
        mock_repository = _create_mock_repository()
        mock_repository.delete.side_effect = Exception("Database connection failed")
        mock_factory = _create_mock_model_factory()
        mock_keyword_generator = _create_mock_keyword_generator()

        service = EssaySearchService(
            repository=mock_repository,
            model_factory=mock_factory,
            keyword_generator=mock_keyword_generator,
        )

        with pytest.raises(Exception) as exc_info:
            service.delete(42)

        assert "Database connection failed" in str(exc_info.value)
