"""Repository interface for CV operations."""

from typing import Optional, Protocol


class ICVRepository(Protocol):
    """
    Interface for CV repository operations.

    This interface defines the contract for CV repository implementations.
    CV repositories manage CV data stored as strings.
    """

    def create(self, cv_data: str) -> str:
        """
        Create or overwrite the CV.

        Args:
            cv_data: CV data as string

        Returns:
            The created CV data

        Raises:
            IOError: If CV cannot be written
        """
        ...

    def find(self) -> Optional[str]:
        """
        Find and return the CV data.

        Returns:
            CV data as string if exists, None otherwise
        """
        ...

    def update(self, cv_data: str) -> str:
        """
        Update the CV with new data.

        Args:
            cv_data: Updated CV data as string

        Returns:
            The updated CV data

        Raises:
            IOError: If CV cannot be written
        """
        ...
