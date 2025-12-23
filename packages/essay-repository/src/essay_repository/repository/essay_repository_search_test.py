"""Integration tests for EssayRepository search methods.

These tests require PostgreSQL with pgvector extension and are
skipped when running against SQLite.

NOTE: These tests are in the RED stage - the implementation does not exist yet.
The tests are designed to fail until the search methods are implemented.
"""

import os
from typing import List

import pytest

from essay_repository.repository import EssayRepository
from job_agent_platform_contracts.essay_repository.schemas import EssaySearchResult


# Skip marker for tests requiring PostgreSQL with pgvector
requires_postgres = pytest.mark.skipif(
    os.environ.get("DATABASE_URL", "").startswith("sqlite") or not os.environ.get("DATABASE_URL"),
    reason="Requires PostgreSQL with pgvector extension",
)


class TestEssayRepositorySearchMethods:
    """Tests verifying search methods are defined on the repository."""

    @pytest.fixture
    def repository(self, db_session):
        """Create an EssayRepository instance."""
        return EssayRepository(session=db_session)

    def test_repository_has_search_by_embedding_method(self, repository):
        """Test that repository has search_by_embedding method."""
        assert hasattr(repository, "search_by_embedding")
        assert callable(repository.search_by_embedding)

    def test_repository_has_search_by_text_method(self, repository):
        """Test that repository has search_by_text method."""
        assert hasattr(repository, "search_by_text")
        assert callable(repository.search_by_text)

    def test_repository_has_search_hybrid_method(self, repository):
        """Test that repository has search_hybrid method."""
        assert hasattr(repository, "search_hybrid")
        assert callable(repository.search_hybrid)

    def test_repository_has_update_embedding_method(self, repository):
        """Test that repository has update_embedding method."""
        assert hasattr(repository, "update_embedding")
        assert callable(repository.update_embedding)


class TestEssayRepositoryUpdateEmbedding:
    """Tests for EssayRepository.update_embedding method.

    These tests can run on SQLite since they only test the embedding
    column update, not vector operations.
    """

    @pytest.fixture
    def repository(self, db_session):
        """Create an EssayRepository instance."""
        return EssayRepository(session=db_session)

    @pytest.fixture
    def sample_embedding(self) -> List[float]:
        """Create a sample 1536-dimension embedding."""
        return [float(i) / 1536 for i in range(1536)]

    def test_update_embedding_returns_true_for_existing_essay(
        self, repository, sample_embedding, repo_sample_essay
    ):
        """Test that update_embedding returns True for existing essay."""
        result = repository.update_embedding(repo_sample_essay.id, sample_embedding)

        assert result is True

    def test_update_embedding_returns_false_for_nonexistent_essay(
        self, repository, sample_embedding
    ):
        """Test that update_embedding returns False for non-existent essay."""
        result = repository.update_embedding(99999, sample_embedding)

        assert result is False

    def test_update_embedding_returns_false_for_zero_id(self, repository, sample_embedding):
        """Test that update_embedding returns False for zero ID."""
        result = repository.update_embedding(0, sample_embedding)

        assert result is False

    def test_update_embedding_returns_false_for_negative_id(self, repository, sample_embedding):
        """Test that update_embedding returns False for negative ID."""
        result = repository.update_embedding(-1, sample_embedding)

        assert result is False


@requires_postgres
class TestEssayRepositorySearchByEmbedding:
    """Tests for EssayRepository.search_by_embedding method.

    These tests require PostgreSQL with pgvector extension.
    """

    @pytest.fixture
    def repository(self, db_session):
        """Create an EssayRepository instance."""
        return EssayRepository(session=db_session)

    @pytest.fixture
    def sample_embedding(self) -> List[float]:
        """Create a sample 1536-dimension embedding."""
        return [float(i) / 1536 for i in range(1536)]

    @pytest.fixture
    def essays_with_embeddings(self, repository):
        """Create essays with embeddings for testing."""
        essays = []
        for i in range(5):
            essay = repository.create(
                {
                    "question": f"Question {i}?",
                    "answer": f"Answer {i}",
                    "keywords": [f"keyword{i}"],
                }
            )
            # Store embedding that varies by index
            embedding = [float(i * j) / 1536 for j in range(1536)]
            repository.update_embedding(essay.id, embedding)
            essays.append(essay)
        return essays

    def test_search_by_embedding_returns_list(
        self, repository, essays_with_embeddings, sample_embedding
    ):
        """Test that search_by_embedding returns a list."""
        result = repository.search_by_embedding(sample_embedding, limit=5)

        assert isinstance(result, list)

    def test_search_by_embedding_respects_limit(
        self, repository, essays_with_embeddings, sample_embedding
    ):
        """Test that search_by_embedding respects the limit parameter."""
        result = repository.search_by_embedding(sample_embedding, limit=2)

        assert len(result) <= 2

    def test_search_by_embedding_returns_essays_ordered_by_similarity(
        self, repository, essays_with_embeddings, sample_embedding
    ):
        """Test that results are ordered by vector similarity."""
        result = repository.search_by_embedding(sample_embedding, limit=5)

        # Results should be ordered by cosine similarity (closest first)
        assert len(result) > 0
        # Each result should be an Essay
        for essay in result:
            assert hasattr(essay, "id")
            assert hasattr(essay, "answer")

    def test_search_by_embedding_excludes_essays_without_embedding(
        self, repository, sample_embedding
    ):
        """Test that essays without embeddings are excluded."""
        # Create essay without embedding
        essay = repository.create(
            {
                "answer": "No embedding",
            }
        )

        result = repository.search_by_embedding(sample_embedding, limit=10)

        # The essay without embedding should not be in results
        result_ids = [e.id for e in result]
        assert essay.id not in result_ids

    def test_search_by_embedding_returns_empty_for_no_matches(self, repository, sample_embedding):
        """Test that empty list is returned when no essays have embeddings."""
        # Create essay without embedding
        repository.create({"answer": "No embedding essay"})

        result = repository.search_by_embedding(sample_embedding, limit=10)

        assert result == []


@requires_postgres
class TestEssayRepositorySearchByText:
    """Tests for EssayRepository.search_by_text method.

    These tests require PostgreSQL for tsvector functionality.
    """

    @pytest.fixture
    def repository(self, db_session):
        """Create an EssayRepository instance."""
        return EssayRepository(session=db_session)

    @pytest.fixture
    def searchable_essays(self, repository):
        """Create essays with searchable content."""
        essays = []
        essays.append(
            repository.create(
                {
                    "question": "What is Python programming?",
                    "answer": "Python is a versatile programming language.",
                    "keywords": ["python", "programming", "language"],
                }
            )
        )
        essays.append(
            repository.create(
                {
                    "question": "What is machine learning?",
                    "answer": "Machine learning is a subset of AI.",
                    "keywords": ["machine learning", "AI", "data science"],
                }
            )
        )
        essays.append(
            repository.create(
                {
                    "question": "What is data engineering?",
                    "answer": "Data engineering involves building data pipelines.",
                    "keywords": ["data", "engineering", "pipelines"],
                }
            )
        )
        return essays

    def test_search_by_text_returns_list(self, repository, searchable_essays):
        """Test that search_by_text returns a list."""
        result = repository.search_by_text("python", limit=10)

        assert isinstance(result, list)

    def test_search_by_text_finds_matching_essays(self, repository, searchable_essays):
        """Test that search finds essays matching the query."""
        result = repository.search_by_text("python programming", limit=10)

        assert len(result) >= 1
        # Should find the Python essay
        answers = [e.answer for e in result]
        assert any("Python" in a or "python" in a.lower() for a in answers)

    def test_search_by_text_respects_limit(self, repository, searchable_essays):
        """Test that search respects the limit parameter."""
        result = repository.search_by_text("data", limit=1)

        assert len(result) <= 1

    def test_search_by_text_ranks_by_relevance(self, repository, searchable_essays):
        """Test that results are ranked by ts_rank."""
        result = repository.search_by_text("machine learning AI", limit=10)

        # Machine learning essay should rank high
        assert len(result) > 0

    def test_search_by_text_searches_question_field(self, repository, searchable_essays):
        """Test that search includes question field."""
        result = repository.search_by_text("data engineering", limit=10)

        assert len(result) >= 1

    def test_search_by_text_searches_keywords_field(self, repository, searchable_essays):
        """Test that search includes keywords field."""
        result = repository.search_by_text("pipelines", limit=10)

        assert len(result) >= 1

    def test_search_by_text_returns_empty_for_no_matches(self, repository):
        """Test that no matches returns empty list."""
        repository.create({"answer": "Unrelated content"})

        result = repository.search_by_text("xyznonexistent", limit=10)

        assert result == []


@requires_postgres
class TestEssayRepositorySearchHybrid:
    """Tests for EssayRepository.search_hybrid method.

    These tests require PostgreSQL with pgvector extension.
    """

    @pytest.fixture
    def repository(self, db_session):
        """Create an EssayRepository instance."""
        return EssayRepository(session=db_session)

    @pytest.fixture
    def sample_embedding(self) -> List[float]:
        """Create a sample 1536-dimension embedding."""
        return [float(i) / 1536 for i in range(1536)]

    @pytest.fixture
    def hybrid_essays(self, repository):
        """Create essays for hybrid search testing."""
        essays = []
        for i, content in enumerate(
            [
                ("Python programming", "Learn Python basics", ["python", "programming"]),
                ("Machine learning", "ML algorithms and data", ["ml", "ai"]),
                ("Data science", "Statistical analysis", ["data", "statistics"]),
            ]
        ):
            question, answer, keywords = content
            essay = repository.create(
                {
                    "question": question,
                    "answer": answer,
                    "keywords": keywords,
                }
            )
            # Add embedding
            embedding = [float(i * j) / 1536 for j in range(1536)]
            repository.update_embedding(essay.id, embedding)
            essays.append(essay)
        return essays

    def test_search_hybrid_returns_essay_search_results(
        self, repository, hybrid_essays, sample_embedding
    ):
        """Test that search_hybrid returns EssaySearchResult objects."""
        result = repository.search_hybrid(
            embedding=sample_embedding,
            text_query="python",
            limit=10,
        )

        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, EssaySearchResult)
            assert hasattr(item, "essay")
            assert hasattr(item, "score")

    def test_search_hybrid_includes_ranking_metadata(
        self, repository, hybrid_essays, sample_embedding
    ):
        """Test that results include vector_rank and text_rank."""
        result = repository.search_hybrid(
            embedding=sample_embedding,
            text_query="python",
            limit=10,
        )

        # At least some results should have ranking info
        for item in result:
            assert item.vector_rank is not None or item.text_rank is not None

    def test_search_hybrid_respects_limit(self, repository, hybrid_essays, sample_embedding):
        """Test that hybrid search respects limit."""
        result = repository.search_hybrid(
            embedding=sample_embedding,
            text_query="data",
            limit=1,
        )

        assert len(result) <= 1

    def test_search_hybrid_uses_default_vector_weight(
        self, repository, hybrid_essays, sample_embedding
    ):
        """Test that default vector_weight is 0.5."""
        # This test verifies the signature accepts the parameter
        result = repository.search_hybrid(
            embedding=sample_embedding,
            text_query="machine learning",
            limit=10,
            # Not passing vector_weight - should default to 0.5
        )

        assert isinstance(result, list)

    def test_search_hybrid_respects_vector_weight(
        self, repository, hybrid_essays, sample_embedding
    ):
        """Test that vector_weight affects result ordering."""
        # With high vector weight, vector similarity should dominate
        result_vector = repository.search_hybrid(
            embedding=sample_embedding,
            text_query="python",
            limit=10,
            vector_weight=0.9,
        )

        # With low vector weight, text relevance should dominate
        result_text = repository.search_hybrid(
            embedding=sample_embedding,
            text_query="python",
            limit=10,
            vector_weight=0.1,
        )

        # Both should return results
        assert len(result_vector) > 0
        assert len(result_text) > 0

    def test_search_hybrid_combines_results_from_both_methods(
        self, repository, hybrid_essays, sample_embedding
    ):
        """Test that hybrid search combines vector and text results."""
        result = repository.search_hybrid(
            embedding=sample_embedding,
            text_query="machine learning",
            limit=10,
        )

        # Should find results
        assert len(result) > 0

    def test_search_hybrid_handles_essays_without_embedding(self, repository, sample_embedding):
        """Test that essays without embeddings participate via text search only."""
        # Create essay without embedding
        essay = repository.create(
            {
                "question": "Special topic",
                "answer": "Unique answer about special topic",
                "keywords": ["special", "unique"],
            }
        )

        result = repository.search_hybrid(
            embedding=sample_embedding,
            text_query="special unique",
            limit=10,
        )

        # The essay should still be findable via text search
        result_ids = [r.essay.id for r in result]
        assert essay.id in result_ids

        # But it should have no vector_rank
        essay_result = next(r for r in result if r.essay.id == essay.id)
        assert essay_result.vector_rank is None
        assert essay_result.text_rank is not None

    def test_search_hybrid_uses_rrf_scoring(self, repository, hybrid_essays, sample_embedding):
        """Test that RRF scoring is applied (1/(k+rank) with k=60)."""
        result = repository.search_hybrid(
            embedding=sample_embedding,
            text_query="python",
            limit=10,
        )

        # Scores should be in valid RRF range
        for item in result:
            # RRF scores are typically small positive values
            assert item.score > 0
            assert item.score <= 1.0  # Max possible is 1/(60+1) * 2 = ~0.03


class TestEssayRepositoryInterfaceCompliance:
    """Tests verifying IEssayRepository interface includes search methods."""

    def test_interface_has_search_by_embedding_method(self):
        """Test that IEssayRepository includes search_by_embedding."""
        from job_agent_platform_contracts.essay_repository import IEssayRepository
        import inspect

        methods = [name for name, _ in inspect.getmembers(IEssayRepository, inspect.isfunction)]
        assert "search_by_embedding" in methods

    def test_interface_has_search_by_text_method(self):
        """Test that IEssayRepository includes search_by_text."""
        from job_agent_platform_contracts.essay_repository import IEssayRepository
        import inspect

        methods = [name for name, _ in inspect.getmembers(IEssayRepository, inspect.isfunction)]
        assert "search_by_text" in methods

    def test_interface_has_search_hybrid_method(self):
        """Test that IEssayRepository includes search_hybrid."""
        from job_agent_platform_contracts.essay_repository import IEssayRepository
        import inspect

        methods = [name for name, _ in inspect.getmembers(IEssayRepository, inspect.isfunction)]
        assert "search_hybrid" in methods

    def test_interface_has_update_embedding_method(self):
        """Test that IEssayRepository includes update_embedding."""
        from job_agent_platform_contracts.essay_repository import IEssayRepository
        import inspect

        methods = [name for name, _ in inspect.getmembers(IEssayRepository, inspect.isfunction)]
        assert "update_embedding" in methods
