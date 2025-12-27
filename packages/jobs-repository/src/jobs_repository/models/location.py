"""Location model."""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jobs_repository.models.base import Base

if TYPE_CHECKING:
    from jobs_repository.models.job import Job


class Location(Base):
    """Location model."""

    __tablename__ = "locations"
    __table_args__ = {"schema": "jobs"}

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    region: Mapped[str] = mapped_column(String(300), unique=True, index=True)

    jobs: Mapped[list["Job"]] = relationship(back_populates="location_rel")

    def __repr__(self) -> str:
        """String representation of Location."""
        return f"<Location(id={self.id}, region='{self.region}')>"
