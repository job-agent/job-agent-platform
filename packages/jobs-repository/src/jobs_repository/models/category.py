"""Category model."""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jobs_repository.models.base import Base

if TYPE_CHECKING:
    from jobs_repository.models.job import Job


class Category(Base):
    """Category model."""

    __tablename__ = "categories"
    __table_args__ = {"schema": "jobs"}

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)

    jobs: Mapped[list["Job"]] = relationship(back_populates="category_rel")

    def __repr__(self) -> str:
        """String representation of Category."""
        return f"<Category(id={self.id}, name='{self.name}')>"
