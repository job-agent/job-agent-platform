"""Service for essay search operations with auto-embedding generation.

This module provides the EssaySearchService class that wraps repository operations
and adds automatic embedding generation for hybrid search functionality.
"""

import logging
from typing import List, Optional, Tuple

from job_agent_platform_contracts.essay_repository import (
    IEssayRepository,
    Essay,
    EssayCreate,
    EssayUpdate,
    EssaySearchResult,
)
from job_agent_backend.contracts import IModelFactory


logger = logging.getLogger(__name__)


class EssaySearchService:
    """Service that provides hybrid search and auto-embedding for essays.

    This service wraps the essay repository and automatically generates
    embeddings when essays are created or updated. It also provides
    hybrid search combining vector similarity and full-text search.
    """

    def __init__(
        self,
        repository: IEssayRepository,
        model_factory: IModelFactory,
    ):
        """Initialize the search service.

        Args:
            repository: Essay repository for CRUD operations
            model_factory: Factory for retrieving embedding model
        """
        self._repository = repository
        self._model_factory = model_factory

    def search(
        self,
        query: str,
        limit: int = 10,
        vector_weight: float = 0.5,
    ) -> List[EssaySearchResult]:
        """Search essays using hybrid vector + text search.

        Args:
            query: Search query string
            limit: Maximum number of results to return
            vector_weight: Weight for vector similarity (0.0 to 1.0).
                          Text weight is (1 - vector_weight). Default 0.5.

        Returns:
            List of EssaySearchResult ordered by combined RRF score
        """
        # Validate query
        trimmed_query = query.strip()
        if not trimmed_query:
            return []

        # Validate limit
        if limit <= 0:
            return []

        # Generate query embedding
        embedding = self._get_embedding(trimmed_query)

        # Perform hybrid search
        return self._repository.search_hybrid(
            embedding=embedding,
            text_query=trimmed_query,
            limit=limit,
            vector_weight=vector_weight,
        )

    def create(self, essay_data: EssayCreate) -> Essay:
        """Create a new essay with auto-generated embedding.

        Args:
            essay_data: Essay data including question, answer, keywords

        Returns:
            Created Essay with embedding stored
        """
        # Create the essay first
        essay = self._repository.create(essay_data)

        # Generate and store embedding
        try:
            text = self._build_embedding_text(
                question=essay_data.get("question"),
                answer=essay_data.get("answer"),
                keywords=essay_data.get("keywords"),
            )
            embedding = self._get_embedding(text)
            self._repository.update_embedding(essay.id, embedding)
        except Exception as e:
            logger.warning(f"Failed to generate embedding for essay {essay.id}: {e}")

        return essay

    def update(
        self,
        essay_id: int,
        essay_data: EssayUpdate,
    ) -> Optional[Essay]:
        """Update an essay and regenerate its embedding.

        Args:
            essay_id: ID of the essay to update
            essay_data: Update data

        Returns:
            Updated Essay if found, None otherwise
        """
        # Update the essay
        essay = self._repository.update(essay_id, essay_data)

        if essay is None:
            return None

        # Regenerate embedding
        try:
            text = self._build_embedding_text(
                question=essay.question,
                answer=essay.answer,
                keywords=essay.keywords,
            )
            embedding = self._get_embedding(text)
            self._repository.update_embedding(essay.id, embedding)
        except Exception as e:
            logger.warning(f"Failed to regenerate embedding for essay {essay.id}: {e}")

        return essay

    def get_paginated(self, page: int, page_size: int) -> Tuple[List[Essay], int]:
        """Get essays with pagination.

        Args:
            page: Page number (1-based)
            page_size: Number of essays per page

        Returns:
            Tuple of (list of essays for the page, total count of all essays)
        """
        return self._repository.get_paginated(page=page, page_size=page_size)

    def backfill_embeddings(self) -> int:
        """Generate embeddings for all essays without one.

        Returns:
            Number of essays updated
        """
        # Get all essays and filter to those without embeddings
        essays = self._repository.get_all()
        updated_count = 0

        for essay in essays:
            try:
                text = self._build_embedding_text(
                    question=essay.question,
                    answer=essay.answer,
                    keywords=essay.keywords,
                )
                embedding = self._get_embedding(text)
                if self._repository.update_embedding(essay.id, embedding):
                    updated_count += 1
            except Exception as e:
                logger.warning(f"Failed to backfill embedding for essay {essay.id}: {e}")

        return updated_count

    def _build_embedding_text(
        self,
        question: Optional[str],
        answer: Optional[str],
        keywords: Optional[List[str]],
    ) -> str:
        """Build text for embedding from essay fields.

        Args:
            question: The essay question
            answer: The essay answer
            keywords: List of keywords

        Returns:
            Concatenated text for embedding
        """
        parts = []

        if question:
            parts.append(question)

        if answer:
            parts.append(answer)

        if keywords:
            parts.append(" ".join(keywords))

        return " ".join(parts)

    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using the model factory.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        model = self._model_factory.get_model(model_id="embedding")
        return model.embed_query(text)
