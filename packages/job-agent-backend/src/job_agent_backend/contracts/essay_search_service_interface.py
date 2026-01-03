"""Interface for essay search service."""

from typing import List, Optional, Protocol, Tuple

from job_agent_platform_contracts.essay_repository import (
    Essay,
    EssayCreate,
    EssayUpdate,
    EssaySearchResult,
)


class IEssaySearchService(Protocol):
    """Interface for essay search service with hybrid search and auto-embedding."""

    def search(
        self,
        query: str,
        limit: int = 10,
        vector_weight: float = 0.5,
    ) -> List[EssaySearchResult]:
        """Search essays using hybrid vector + text search."""
        ...

    def create(self, essay_data: EssayCreate) -> Essay:
        """Create a new essay with auto-generated embedding."""
        ...

    def update(self, essay_id: int, essay_data: EssayUpdate) -> Optional[Essay]:
        """Update an essay and regenerate its embedding."""
        ...

    def backfill_embeddings(self) -> int:
        """Generate embeddings for all essays without one."""
        ...

    def get_paginated(self, page: int, page_size: int) -> Tuple[List[Essay], int]:
        """Get essays with pagination.

        Args:
            page: Page number (1-based)
            page_size: Number of essays per page

        Returns:
            Tuple of (list of essays for the page, total count of all essays)
        """
        ...

    def delete(self, essay_id: int) -> bool:
        """Delete an essay by ID.

        Args:
            essay_id: ID of the essay to delete

        Returns:
            True if the essay was deleted, False if not found
        """
        ...
