"""Company model."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from jobs_repository.models.base import Base


class Company(Base):
    """Company model."""

    __tablename__ = "companies"
    __table_args__ = {"schema": "jobs"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(300), nullable=False, unique=True, index=True)
    website = Column(String(500), nullable=True)

    jobs = relationship("Job", back_populates="company_rel")

    def __repr__(self) -> str:
        """String representation of Company."""
        return f"<Company(id={self.id}, name='{self.name}')>"
