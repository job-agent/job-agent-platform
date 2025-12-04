"""Industry model."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from jobs_repository.models.base import Base


class Industry(Base):
    """Industry model."""

    __tablename__ = "industries"
    __table_args__ = {"schema": "jobs"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False, unique=True, index=True)

    jobs = relationship("Job", back_populates="industry_rel")

    def __repr__(self) -> str:
        """String representation of Industry."""
        return f"<Industry(id={self.id}, name='{self.name}')>"
