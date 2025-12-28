"""Job model."""

from datetime import datetime, UTC
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jobs_repository.models.base import Base

if TYPE_CHECKING:
    from jobs_repository.models.company import Company
    from jobs_repository.models.location import Location
    from jobs_repository.models.category import Category
    from jobs_repository.models.industry import Industry


class Job(Base):
    """Job listing model."""

    __tablename__ = "jobs"
    __table_args__ = {"schema": "jobs"}

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(500), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    must_have_skills: Mapped[Optional[list[list[str]]]] = mapped_column(JSONB, nullable=True)
    nice_to_have_skills: Mapped[Optional[list[list[str]]]] = mapped_column(JSONB, nullable=True)

    company_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("jobs.companies.id"), index=True, nullable=True
    )
    location_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("jobs.locations.id"), index=True, nullable=True
    )
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("jobs.categories.id"), index=True, nullable=True
    )
    industry_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("jobs.industries.id"), index=True, nullable=True
    )

    job_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    experience_months: Mapped[Optional[int]] = mapped_column(nullable=True)
    salary_min: Mapped[Optional[float]] = mapped_column(nullable=True)
    salary_max: Mapped[Optional[float]] = mapped_column(nullable=True)
    salary_currency: Mapped[Optional[str]] = mapped_column(String(10), default="USD", nullable=True)

    external_id: Mapped[Optional[str]] = mapped_column(
        String(300), unique=True, index=True, nullable=True
    )
    source: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_remote: Mapped[bool] = mapped_column(default=False, index=True)
    is_relevant: Mapped[bool] = mapped_column(default=True, index=True)
    is_filtered: Mapped[bool] = mapped_column(default=False, index=True)
    posted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    company_rel: Mapped[Optional["Company"]] = relationship(back_populates="jobs")
    location_rel: Mapped[Optional["Location"]] = relationship(back_populates="jobs")
    category_rel: Mapped[Optional["Category"]] = relationship(back_populates="jobs")
    industry_rel: Mapped[Optional["Industry"]] = relationship(back_populates="jobs")

    def __repr__(self) -> str:
        """String representation of Job."""
        company_name = self.company_rel.name if self.company_rel else "Unknown"
        return f"<Job(id={self.id}, title='{self.title}', company='{company_name}')>"
