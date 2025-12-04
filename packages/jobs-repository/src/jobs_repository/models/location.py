"""Location model."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from jobs_repository.models.base import Base


class Location(Base):
    """Location model."""

    __tablename__ = "locations"
    __table_args__ = {"schema": "jobs"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    region = Column(String(300), nullable=False, unique=True, index=True)

    jobs = relationship("Job", back_populates="location_rel")

    def __repr__(self) -> str:
        """String representation of Location."""
        return f"<Location(id={self.id}, region='{self.region}')>"
