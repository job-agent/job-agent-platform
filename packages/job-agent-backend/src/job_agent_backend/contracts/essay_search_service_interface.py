"""Interface for essay search service."""

from abc import ABC, abstractmethod
from typing import List, Optional

from job_agent_platform_contracts.essay_repository import (
    Essay,
    EssayCreate,
    EssayUpdate,
    EssaySearchResult,
)


class IEssaySearchService(ABC):
    """Interface for essay search service with hybrid search and auto-embedding."""

    @abstractmethod
    def search(
        self,
        query: str,
        limit: int = 10,
        vector_weight: float = 0.5,
    ) -> List[EssaySearchResult]:
        """Search essays using hybrid vector + text search."""
        pass

    @abstractmethod
    def create(self, essay_data: EssayCreate) -> Essay:
        """Create a new essay with auto-generated embedding."""
        pass

    @abstractmethod
    def update(self, essay_id: int, essay_data: EssayUpdate) -> Optional[Essay]:
        """Update an essay and regenerate its embedding."""
        pass

    @abstractmethod
    def backfill_embeddings(self) -> int:
        """Generate embeddings for all essays without one."""
        pass
