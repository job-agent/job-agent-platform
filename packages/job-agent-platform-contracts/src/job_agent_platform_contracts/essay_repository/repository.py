"""Repository interface for essay operations."""

from typing import List, Optional, Protocol, runtime_checkable

from job_agent_platform_contracts.essay_repository.schemas import (
    EssayCreate,
    EssayUpdate,
    Essay,
    EssaySearchResult,
)


@runtime_checkable
class IEssayRepository(Protocol):
    """
    Interface for essay repository operations.

    This interface defines the contract that all essay repository implementations
    must follow, ensuring consistency across different storage backends.
    """

    def create(self, essay_data: EssayCreate) -> Essay:
        """
        Create a new essay from an `EssayCreate` payload.

        Args:
            essay_data: Typed dictionary describing the essay to persist.

        Returns:
            Created essay entity

        Raises:
            EssayValidationError: If data validation fails (e.g., missing answer)
            TransactionError: If database transaction fails
        """
        ...

    def get_by_id(self, essay_id: int) -> Optional[Essay]:
        """
        Get essay by ID.

        Args:
            essay_id: The essay's primary key identifier

        Returns:
            Essay entity if found, None otherwise
        """
        ...

    def get_all(self) -> List[Essay]:
        """
        Get all essays.

        Returns:
            List of Essay entities (may be empty)
        """
        ...

    def delete(self, essay_id: int) -> bool:
        """
        Delete an essay by ID.

        Args:
            essay_id: The essay's primary key identifier

        Returns:
            True if deleted, False if not found
        """
        ...

    def update(self, essay_id: int, essay_data: EssayUpdate) -> Optional[Essay]:
        """
        Update an existing essay.

        Args:
            essay_id: The essay's primary key identifier
            essay_data: Typed dictionary with fields to update

        Returns:
            Updated Essay if found, None if not found

        Raises:
            EssayValidationError: If data validation fails
            TransactionError: If database transaction fails
        """
        ...

    def search_by_embedding(self, embedding: List[float], limit: int) -> List[Essay]:
        """
        Search essays by vector similarity.

        Args:
            embedding: The query embedding vector (1536 dimensions)
            limit: Maximum number of results to return

        Returns:
            List of Essay entities ordered by cosine similarity
        """
        ...

    def search_by_text(self, query: str, limit: int) -> List[Essay]:
        """
        Search essays by full-text search.

        Args:
            query: The text query
            limit: Maximum number of results to return

        Returns:
            List of Essay entities ordered by text relevance
        """
        ...

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

        Uses Reciprocal Rank Fusion (RRF) to combine results, then
        Maximal Marginal Relevance (MMR) to diversify the final results.

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
        """
        ...

    def update_embedding(self, essay_id: int, embedding: List[float]) -> bool:
        """
        Update the embedding for an essay.

        Args:
            essay_id: The essay's primary key identifier
            embedding: The embedding vector (1536 dimensions)

        Returns:
            True if updated, False if essay not found
        """
        ...

    def update_keywords(self, essay_id: int, keywords: List[str]) -> bool:
        """
        Update the keywords for an essay.

        Args:
            essay_id: The essay's primary key identifier
            keywords: List of keywords to set

        Returns:
            True if updated, False if essay not found
        """
        ...
