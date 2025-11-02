"""Database models for job listings."""

from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from jobs_repository.database.base import Base


class Job(Base):
    """Job listing model."""

    __tablename__ = "jobs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Job basic information
    title = Column(String(500), nullable=False, index=True)
    company = Column(String(300), nullable=False, index=True)
    location = Column(String(300), nullable=True)
    description = Column(Text, nullable=True)

    # Job details
    job_type = Column(String(100), nullable=True)  # e.g., "Full-time", "Part-time", "Contract"
    experience_level = Column(String(100), nullable=True)  # e.g., "Junior", "Mid", "Senior"
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(10), nullable=True, default="USD")

    # External references
    external_id = Column(String(300), unique=True, index=True, nullable=True)
    source = Column(String(100), nullable=True, index=True)  # e.g., "LinkedIn", "Indeed"
    source_url = Column(Text, nullable=True)

    # Status and metadata
    is_active = Column(Boolean, default=True, index=True)
    is_remote = Column(Boolean, default=False, index=True)
    posted_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Additional data stored as JSON
    extra_data = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __repr__(self) -> str:
        """String representation of Job."""
        return f"<Job(id={self.id}, title='{self.title}', company='{self.company}')>"

    def to_dict(self) -> dict:
        """Convert job to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "description": self.description,
            "job_type": self.job_type,
            "experience_level": self.experience_level,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "salary_currency": self.salary_currency,
            "external_id": self.external_id,
            "source": self.source,
            "source_url": self.source_url,
            "is_active": self.is_active,
            "is_remote": self.is_remote,
            "posted_at": self.posted_at.isoformat() if self.posted_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "extra_data": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
