"""Interface for reference data service."""

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from jobs_repository.models import Company, Location, Category, Industry


class IReferenceDataService(ABC):
    """Service for managing reference data entities."""

    @abstractmethod
    def get_or_create_company(self, session: Session, name: str) -> Company:
        """Get existing company or create new one."""

    @abstractmethod
    def get_or_create_location(self, session: Session, region: str) -> Location:
        """Get existing location or create new one."""

    @abstractmethod
    def get_or_create_category(self, session: Session, name: str) -> Category:
        """Get existing category or create new one."""

    @abstractmethod
    def get_or_create_industry(self, session: Session, name: str) -> Industry:
        """Get existing industry or create new one."""
