"""Industry model."""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jobs_repository.models.base import Base

if TYPE_CHECKING:
    from jobs_repository.models.job import Job


class Industry(Base):
    """Industry model."""

    __tablename__ = "industries"
    __table_args__ = {"schema": "jobs"}

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)

    jobs: Mapped[list["Job"]] = relationship(back_populates="industry_rel")

    def __repr__(self) -> str:
        """String representation of Industry."""
        return f"<Industry(id={self.id}, name='{self.name}')>"
