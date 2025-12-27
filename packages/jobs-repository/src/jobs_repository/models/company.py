"""Company model."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jobs_repository.models.base import Base

if TYPE_CHECKING:
    from jobs_repository.models.job import Job


class Company(Base):
    """Company model."""

    __tablename__ = "companies"
    __table_args__ = {"schema": "jobs"}

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(300), unique=True, index=True)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    jobs: Mapped[list["Job"]] = relationship(back_populates="company_rel")

    def __repr__(self) -> str:
        """String representation of Company."""
        return f"<Company(id={self.id}, name='{self.name}')>"
