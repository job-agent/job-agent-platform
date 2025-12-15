"""Job model."""

from datetime import datetime, UTC

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from jobs_repository.models.base import Base


class Job(Base):
    """Job listing model."""

    __tablename__ = "jobs"
    __table_args__ = {"schema": "jobs"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=True)
    must_have_skills = Column(ARRAY(String), nullable=True)
    nice_to_have_skills = Column(ARRAY(String), nullable=True)

    company_id = Column(Integer, ForeignKey("jobs.companies.id"), nullable=True, index=True)
    location_id = Column(Integer, ForeignKey("jobs.locations.id"), nullable=True, index=True)
    category_id = Column(Integer, ForeignKey("jobs.categories.id"), nullable=True, index=True)
    industry_id = Column(Integer, ForeignKey("jobs.industries.id"), nullable=True, index=True)

    job_type = Column(String(100), nullable=True)
    experience_months = Column(Integer, nullable=True)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(10), nullable=True, default="USD")

    external_id = Column(String(300), unique=True, index=True, nullable=True)
    source = Column(String(100), nullable=True, index=True)
    source_url = Column(Text, nullable=True)

    is_remote = Column(Boolean, default=False, index=True)
    is_relevant = Column(Boolean, default=True, nullable=False, index=True)
    is_filtered = Column(Boolean, default=False, nullable=False, index=True)
    posted_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    company_rel = relationship("Company", back_populates="jobs")
    location_rel = relationship("Location", back_populates="jobs")
    category_rel = relationship("Category", back_populates="jobs")
    industry_rel = relationship("Industry", back_populates="jobs")

    def __repr__(self) -> str:
        """String representation of Job."""
        company_name = self.company_rel.name if self.company_rel else "Unknown"
        return f"<Job(id={self.id}, title='{self.title}', company='{company_name}')>"
