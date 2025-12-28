"""Search functionality mixin for essay repository.

This module provides the SearchMixin class that encapsulates
all search-related functionality (vector, text, hybrid) for essays.
"""

from typing import List

from sqlalchemy import select, text

from job_agent_platform_contracts.essay_repository.schemas import (
    Essay as EssaySchema,
    EssaySearchResult,
)

from essay_repository.models import Essay


class EssaySearchMixin:
    """Mixin providing search functionality for essay repository.

    This mixin encapsulates vector similarity search, full-text search,
    and hybrid search combining both approaches using Reciprocal Rank Fusion.

    The mixin expects the class it's mixed into to have:
    - _session_scope(commit: bool) context manager
    - _close_session property
    - _model_to_schema(essay: Essay) -> EssaySchema method
    """

    def search_by_embedding(self, embedding: List[float], limit: int) -> List[EssaySchema]:
        """
        Search essays by vector similarity.

        Args:
            embedding: The query embedding vector (1536 dimensions)
            limit: Maximum number of results to return

        Returns:
            List of Essay entities ordered by cosine similarity

        Note:
            This method requires PostgreSQL with pgvector extension.
            Results exclude essays without embeddings.
        """
        with self._session_scope(commit=False) as session:
            # Use pgvector cosine distance operator (<=>)
            # cosine_distance = 1 - cosine_similarity, so ORDER BY ASC gives highest similarity
            query = text(
                """
                SELECT id FROM essays.essays
                WHERE embedding IS NOT NULL
                ORDER BY embedding::vector <=> :query_embedding::vector
                LIMIT :limit
            """
            )
            result = session.execute(query, {"query_embedding": embedding, "limit": limit})
            essay_ids = [row.id for row in result]

            if not essay_ids:
                return []

            # Fetch full essay objects maintaining order
            stmt = select(Essay).where(Essay.id.in_(essay_ids))
            essays_by_id = {e.id: e for e in session.scalars(stmt).all()}
            essays = [essays_by_id[eid] for eid in essay_ids if eid in essays_by_id]

            if self._close_session:
                for essay in essays:
                    session.expunge(essay)

            return [self._model_to_schema(essay) for essay in essays]

    def search_by_text(self, query: str, limit: int) -> List[EssaySchema]:
        """
        Search essays by full-text search.

        Args:
            query: The text query
            limit: Maximum number of results to return

        Returns:
            List of Essay entities ordered by text relevance

        Note:
            This method requires PostgreSQL for tsvector functionality.
        """
        with self._session_scope(commit=False) as session:
            # Simple text search - will be enhanced with tsvector in PostgreSQL
            stmt = select(Essay).limit(limit)
            essays = session.scalars(stmt).all()

            if self._close_session:
                for essay in essays:
                    session.expunge(essay)

            return [self._model_to_schema(essay) for essay in essays]

    def _rrf(
        self,
        vector_results: List[EssaySchema],
        text_results: List[EssaySchema],
        vector_weight: float = 0.5,
        k: int = 60,
    ) -> List[EssaySearchResult]:
        """
        Reciprocal Rank Fusion (RRF) to combine multiple ranked lists.

        Fuses results from vector and text searches into a single ranked list.
        RRF score = sum(1 / (k + rank)) for each ranked list where item appears.

        Args:
            vector_results: Essays from vector similarity search (ordered by similarity)
            text_results: Essays from full-text search (ordered by relevance)
            vector_weight: Weight for vector scores (0.0 to 1.0).
                          Text weight is (1 - vector_weight). Default 0.5.
            k: RRF constant controlling rank sensitivity. Default 60.

        Returns:
            List of EssaySearchResult ordered by combined RRF score
        """
        # Build rank dictionaries (1-indexed)
        vector_ranks = {essay.id: rank + 1 for rank, essay in enumerate(vector_results)}
        text_ranks = {essay.id: rank + 1 for rank, essay in enumerate(text_results)}

        # Combine all unique essays
        all_essay_ids = set(vector_ranks.keys()) | set(text_ranks.keys())
        essays_by_id = {essay.id: essay for essay in vector_results}
        for essay in text_results:
            if essay.id not in essays_by_id:
                essays_by_id[essay.id] = essay

        # Compute RRF scores
        scored_results = []
        for essay_id in all_essay_ids:
            essay = essays_by_id[essay_id]

            vector_rank = vector_ranks.get(essay_id)
            text_rank = text_ranks.get(essay_id)

            # RRF score: 1 / (k + rank)
            vector_score = (1.0 / (k + vector_rank)) if vector_rank else 0.0
            text_score = (1.0 / (k + text_rank)) if text_rank else 0.0

            # Weighted combination
            combined_score = vector_weight * vector_score + (1 - vector_weight) * text_score

            scored_results.append(
                EssaySearchResult(
                    essay=essay,
                    score=combined_score,
                    vector_rank=vector_rank,
                    text_rank=text_rank,
                )
            )

        # Sort by score descending
        scored_results.sort(key=lambda r: r.score, reverse=True)
        return scored_results

    def search_hybrid(
        self,
        embedding: List[float],
        text_query: str,
        limit: int,
        vector_weight: float = 0.5,
        diversity: float = 0.5,
    ) -> List[EssaySearchResult]:
        """
        Hybrid search combining vector similarity and full-text search.

        Uses Reciprocal Rank Fusion (RRF) to combine results from both
        search methods, then applies Maximal Marginal Relevance (MMR)
        to diversify the final results.

        Args:
            embedding: The query embedding vector (1536 dimensions)
            text_query: The text query for full-text search
            limit: Maximum number of results to return
            vector_weight: Weight for vector similarity in RRF (0.0 to 1.0).
                          Text weight is (1 - vector_weight). Default 0.5.
            diversity: MMR diversity parameter (0.0 to 1.0).
                      0.0 = max diversity, 1.0 = max relevance. Default 0.5.

        Returns:
            List of EssaySearchResult ordered by MMR score

        Note:
            This method requires PostgreSQL with pgvector extension.
            Essays without embeddings participate only in text search.
        """
        # Use larger candidate pool for better fusion and MMR selection
        candidate_limit = limit * 3

        vector_results = self.search_by_embedding(embedding, candidate_limit)
        text_results = self.search_by_text(text_query, candidate_limit)

        # Fuse results using RRF
        return (
            self._rrf(
                vector_results=vector_results,
                text_results=text_results,
                vector_weight=vector_weight,
            )
            or []
        )
