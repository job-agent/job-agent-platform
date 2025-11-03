"""Database models for job listings."""

from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from jobs_repository.database.base import Base


class Company(Base):
    """Company model."""

    __tablename__ = "companies"
    __table_args__ = {"schema": "jobs"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(300), nullable=False, unique=True, index=True)

    # Relationships
    jobs = relationship("Job", back_populates="company_rel")

    def __repr__(self) -> str:
        """String representation of Company."""
        return f"<Company(id={self.id}, name='{self.name}')>"


class Location(Base):
    """Location model."""

    __tablename__ = "locations"
    __table_args__ = {"schema": "jobs"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    region = Column(String(300), nullable=False, unique=True, index=True)

    # Relationships
    jobs = relationship("Job", back_populates="location_rel")

    def __repr__(self) -> str:
        """String representation of Location."""
        return f"<Location(id={self.id}, region='{self.region}')>"


class Category(Base):
    """Category model."""

    __tablename__ = "categories"
    __table_args__ = {"schema": "jobs"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False, unique=True, index=True)

    # Relationships
    jobs = relationship("Job", back_populates="category_rel")

    def __repr__(self) -> str:
        """String representation of Category."""
        return f"<Category(id={self.id}, name='{self.name}')>"


class Industry(Base):
    """Industry model."""

    __tablename__ = "industries"
    __table_args__ = {"schema": "jobs"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False, unique=True, index=True)

    # Relationships
    jobs = relationship("Job", back_populates="industry_rel")

    def __repr__(self) -> str:
        """String representation of Industry."""
        return f"<Industry(id={self.id}, name='{self.name}')>"


class Job(Base):
    """Job listing model."""

    __tablename__ = "jobs"
    __table_args__ = {"schema": "jobs"}

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Job basic information
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Foreign keys to normalized tables
    company_id = Column(Integer, ForeignKey("jobs.companies.id"), nullable=True, index=True)
    location_id = Column(Integer, ForeignKey("jobs.locations.id"), nullable=True, index=True)
    category_id = Column(Integer, ForeignKey("jobs.categories.id"), nullable=True, index=True)
    industry_id = Column(Integer, ForeignKey("jobs.industries.id"), nullable=True, index=True)

    # Job details
    job_type = Column(String(100), nullable=True)  # e.g., "Full-time", "Part-time", "Contract"
    experience_level = Column(String(100), nullable=True)  # e.g., "Junior", "Mid", "Senior"
    experience_months = Column(Integer, nullable=True)  # Required experience in months
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

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    company_rel = relationship("Company", back_populates="jobs")
    location_rel = relationship("Location", back_populates="jobs")
    category_rel = relationship("Category", back_populates="jobs")
    industry_rel = relationship("Industry", back_populates="jobs")

    def __repr__(self) -> str:
        """String representation of Job."""
        company_name = self.company_rel.name if self.company_rel else "Unknown"
        return f"<Job(id={self.id}, title='{self.title}', company='{company_name}')>"

    def to_dict(self) -> dict:
        """Convert job to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "company_id": self.company_id,
            "company_name": self.company_rel.name if self.company_rel else None,
            "location_id": self.location_id,
            "location_region": self.location_rel.region if self.location_rel else None,
            "category_id": self.category_id,
            "category_name": self.category_rel.name if self.category_rel else None,
            "industry_id": self.industry_id,
            "industry_name": self.industry_rel.name if self.industry_rel else None,
            "description": self.description,
            "job_type": self.job_type,
            "experience_level": self.experience_level,
            "experience_months": self.experience_months,
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
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
