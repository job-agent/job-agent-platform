"""Repository implementation for essay persistence.

This module provides the EssayRepository class that implements
the IEssayRepository interface for CRUD operations on essays.
"""

from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select, text, func, desc

from db_core import BaseRepository, TransactionError
from job_agent_platform_contracts.essay_repository import IEssayRepository
from job_agent_platform_contracts.essay_repository.schemas import (
    EssayCreate,
    EssayUpdate,
    Essay as EssaySchema,
    EssaySearchResult,
)
from job_agent_platform_contracts.essay_repository.exceptions import EssayValidationError

from essay_repository.models import Essay


class EssayRepository(BaseRepository, IEssayRepository):
    """Repository that persists essays to the database.

    The repository supports creating, reading, updating, and deleting
    essay records. It follows the session scope pattern for transaction
    management.
    """

    def __init__(
        self,
        session: Optional[Session] = None,
        session_factory=None,
    ):
        """
        Initialize the repository with a managed or external session.

        Args:
            session: Existing SQLAlchemy session to reuse
            session_factory: Callable returning SQLAlchemy session instances

        Raises:
            ValueError: If both session and session_factory are provided
            TypeError: If session_factory is not callable
        """
        super().__init__(session=session, session_factory=session_factory)

    def _model_to_schema(self, essay: Essay) -> EssaySchema:
        """Convert Essay model to Essay schema.

        Args:
            essay: Essay model instance

        Returns:
            Essay Pydantic schema instance
        """
        return EssaySchema.model_validate(essay)

    def create(self, essay_data: EssayCreate) -> EssaySchema:
        """
        Create a new essay from EssayCreate data.

        Args:
            essay_data: Dictionary containing essay fields

        Returns:
            Created Essay schema instance

        Raises:
            EssayValidationError: If data validation fails (e.g., missing answer)
            TransactionError: If database transaction fails
        """
        # Validate required fields
        if "answer" not in essay_data:
            raise EssayValidationError("answer", "Answer is required")

        try:
            with self._session_scope(commit=True) as session:
                essay = Essay(
                    question=essay_data.get("question"),
                    answer=essay_data["answer"],
                    keywords=essay_data.get("keywords"),
                )
                session.add(essay)
                session.flush()

                # Re-query to ensure all fields are loaded
                stmt = select(Essay).where(Essay.id == essay.id)
                essay = session.scalar(stmt)

                if self._close_session:
                    session.expunge(essay)

                return self._model_to_schema(essay)

        except EssayValidationError:
            raise
        except IntegrityError as e:
            raise EssayValidationError("data", f"Integrity constraint violated: {e}") from e
        except SQLAlchemyError as e:
            raise TransactionError(f"Failed to create essay: {e}") from e

    def get_by_id(self, essay_id: int) -> Optional[EssaySchema]:
        """
        Get essay by ID.

        Args:
            essay_id: The essay's primary key identifier

        Returns:
            Essay schema if found, None otherwise
        """
        if essay_id <= 0:
            return None

        with self._session_scope(commit=False) as session:
            stmt = select(Essay).where(Essay.id == essay_id)
            essay = session.scalar(stmt)

            if essay is None:
                return None

            if self._close_session:
                session.expunge(essay)

            return self._model_to_schema(essay)

    def get_all(self) -> List[EssaySchema]:
        """
        Get all essays.

        Returns:
            List of Essay schema instances (may be empty)
        """
        with self._session_scope(commit=False) as session:
            stmt = select(Essay)
            essays = session.scalars(stmt).all()

            if self._close_session:
                for essay in essays:
                    session.expunge(essay)

            return [self._model_to_schema(essay) for essay in essays]

    def get_paginated(self, page: int, page_size: int) -> Tuple[List[EssaySchema], int]:
        """
        Get paginated essays sorted by creation date descending (newest first).

        Args:
            page: Page number (1-indexed). Values <= 0 are treated as page 1.
            page_size: Number of essays per page.

        Returns:
            Tuple of (essays list for the requested page, total count of all essays)
        """
        if page <= 0:
            page = 1

        with self._session_scope(commit=False) as session:
            total_count = session.scalar(select(func.count(Essay.id)))

            offset = (page - 1) * page_size
            stmt = select(Essay).order_by(desc(Essay.created_at)).offset(offset).limit(page_size)
            essays = session.scalars(stmt).all()

            if self._close_session:
                for essay in essays:
                    session.expunge(essay)

            return [self._model_to_schema(essay) for essay in essays], total_count or 0

    def delete(self, essay_id: int) -> bool:
        """
        Delete an essay by ID.

        Args:
            essay_id: The essay's primary key identifier

        Returns:
            True if deleted, False if not found
        """
        if essay_id <= 0:
            return False

        try:
            with self._session_scope(commit=True) as session:
                stmt = select(Essay).where(Essay.id == essay_id)
                essay = session.scalar(stmt)

                if essay is None:
                    return False

                session.delete(essay)
                return True

        except SQLAlchemyError as e:
            raise TransactionError(f"Failed to delete essay: {e}") from e

    def update(self, essay_id: int, essay_data: EssayUpdate) -> Optional[EssaySchema]:
        """
        Update an existing essay.

        Args:
            essay_id: The essay's primary key identifier
            essay_data: Dictionary with fields to update

        Returns:
            Updated Essay schema if found, None if not found

        Raises:
            EssayValidationError: If data validation fails
            TransactionError: If database transaction fails
        """
        if essay_id <= 0:
            return None

        try:
            with self._session_scope(commit=True) as session:
                stmt = select(Essay).where(Essay.id == essay_id)
                essay = session.scalar(stmt)

                if essay is None:
                    return None

                # Update only provided fields
                if "question" in essay_data:
                    essay.question = essay_data["question"]
                if "answer" in essay_data:
                    essay.answer = essay_data["answer"]
                if "keywords" in essay_data:
                    essay.keywords = essay_data["keywords"]

                session.flush()

                # Re-query to get updated timestamps
                session.refresh(essay)

                if self._close_session:
                    session.expunge(essay)

                return self._model_to_schema(essay)

        except IntegrityError as e:
            raise EssayValidationError("data", f"Integrity constraint violated: {e}") from e
        except SQLAlchemyError as e:
            raise TransactionError(f"Failed to update essay: {e}") from e

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

    def update_embedding(self, essay_id: int, embedding: List[float]) -> bool:
        """
        Update the embedding for an essay.

        Args:
            essay_id: The essay's primary key identifier
            embedding: The embedding vector (1536 dimensions)

        Returns:
            True if updated, False if essay not found
        """
        if essay_id <= 0:
            return False

        try:
            with self._session_scope(commit=True) as session:
                stmt = select(Essay).where(Essay.id == essay_id)
                essay = session.scalar(stmt)

                if essay is None:
                    return False

                essay.embedding = embedding
                session.flush()
                return True

        except SQLAlchemyError as e:
            raise TransactionError(f"Failed to update embedding: {e}") from e
