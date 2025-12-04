"""Category model."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from jobs_repository.models.base import Base


class Category(Base):
    """Category model."""

    __tablename__ = "categories"
    __table_args__ = {"schema": "jobs"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False, unique=True, index=True)

    jobs = relationship("Job", back_populates="category_rel")

    def __repr__(self) -> str:
        """String representation of Category."""
        return f"<Category(id={self.id}, name='{self.name}')>"
