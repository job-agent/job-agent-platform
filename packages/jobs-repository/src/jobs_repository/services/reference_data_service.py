"""Service for managing reference data entities."""

from typing import Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from jobs_repository.interfaces import IReferenceDataService
from jobs_repository.models import Company, Location, Category, Industry

T = TypeVar("T", Company, Location, Category, Industry)


class ReferenceDataService(IReferenceDataService):
    """Service that manages lookup and creation of reference data entities."""

    def get_or_create_company(self, session: Session, name: str) -> Company:
        """Get existing company or create new one."""
        return self._get_or_create(session, Company, Company.name == name, {"name": name})

    def get_or_create_location(self, session: Session, region: str) -> Location:
        """Get existing location or create new one."""
        return self._get_or_create(session, Location, Location.region == region, {"region": region})

    def get_or_create_category(self, session: Session, name: str) -> Category:
        """Get existing category or create new one."""
        return self._get_or_create(session, Category, Category.name == name, {"name": name})

    def get_or_create_industry(self, session: Session, name: str) -> Industry:
        """Get existing industry or create new one."""
        return self._get_or_create(session, Industry, Industry.name == name, {"name": name})

    def _get_or_create(self, session: Session, model: Type[T], condition, data: dict) -> T:
        """
        Generic get-or-create method for reference entities.

        Args:
            session: SQLAlchemy session
            model: Model class to query/create
            condition: SQLAlchemy where condition
            data: Data dictionary to create entity with

        Returns:
            Existing or newly created entity
        """
        stmt = select(model).where(condition)
        entity = session.scalar(stmt)

        if entity:
            return entity

        entity = model(**data)
        session.add(entity)
        session.flush()
        return entity
