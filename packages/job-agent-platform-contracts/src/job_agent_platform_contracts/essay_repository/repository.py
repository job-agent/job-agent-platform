"""Repository interface for essay operations."""

from abc import ABC, abstractmethod
from typing import List, Optional

from job_agent_platform_contracts.essay_repository.schemas import (
    EssayCreate,
    EssayUpdate,
    Essay,
)


class IEssayRepository(ABC):
    """
    Interface for essay repository operations.

    This interface defines the contract that all essay repository implementations
    must follow, ensuring consistency across different storage backends.
    """

    @abstractmethod
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
        pass

    @abstractmethod
    def get_by_id(self, essay_id: int) -> Optional[Essay]:
        """
        Get essay by ID.

        Args:
            essay_id: The essay's primary key identifier

        Returns:
            Essay entity if found, None otherwise
        """
        pass

    @abstractmethod
    def get_all(self) -> List[Essay]:
        """
        Get all essays.

        Returns:
            List of Essay entities (may be empty)
        """
        pass

    @abstractmethod
    def delete(self, essay_id: int) -> bool:
        """
        Delete an essay by ID.

        Args:
            essay_id: The essay's primary key identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
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
        pass
