"""Job search schema with query building capabilities."""

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import and_, or_
from sqlalchemy.orm import Query


class JobSearch(BaseModel):
    """Schema for job search parameters with query building."""

    # Text search
    query_text: Optional[str] = Field(None, description="Search text for title or description")

    # Basic filters
    company: Optional[str] = Field(None, description="Filter by company name")
    location: Optional[str] = Field(None, description="Filter by location")
    job_type: Optional[str] = Field(None, description="Filter by job type")
    experience_level: Optional[str] = Field(None, description="Filter by experience level")
    source: Optional[str] = Field(None, description="Filter by source")

    # Boolean filters
    is_remote: Optional[bool] = Field(None, description="Filter by remote status")
    is_active: Optional[bool] = Field(True, description="Filter by active status")

    # ID filters
    external_id: Optional[str] = Field(None, description="Filter by external ID")
    ids: Optional[List[int]] = Field(None, description="Filter by list of IDs")

    # Salary filters
    salary_min_gte: Optional[float] = Field(None, ge=0, description="Minimum salary threshold")
    salary_max_lte: Optional[float] = Field(None, ge=0, description="Maximum salary threshold")

    # Pagination
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of records to return")

    # Sorting
    order_by: str = Field("created_at", description="Field to order by")
    order_desc: bool = Field(True, description="Sort in descending order")

    model_config = ConfigDict(from_attributes=True)

    def build_filters(self, job_model) -> List:
        """
        Build SQLAlchemy filter expressions from search parameters.

        Args:
            job_model: The Job SQLAlchemy model class

        Returns:
            List of SQLAlchemy filter expressions
        """
        filters = []

        # Active status filter
        if self.is_active is not None:
            filters.append(job_model.is_active == self.is_active)

        # Text search (title or description)
        if self.query_text:
            text_filter = or_(
                job_model.title.ilike(f"%{self.query_text}%"),
                job_model.description.ilike(f"%{self.query_text}%"),
            )
            filters.append(text_filter)

        # Company filter
        if self.company:
            filters.append(job_model.company.ilike(f"%{self.company}%"))

        # Location filter
        if self.location:
            filters.append(job_model.location.ilike(f"%{self.location}%"))

        # Job type filter
        if self.job_type:
            filters.append(job_model.job_type == self.job_type)

        # Experience level filter
        if self.experience_level:
            filters.append(job_model.experience_level == self.experience_level)

        # Source filter
        if self.source:
            filters.append(job_model.source == self.source)

        # Remote filter
        if self.is_remote is not None:
            filters.append(job_model.is_remote == self.is_remote)

        # External ID filter
        if self.external_id:
            filters.append(job_model.external_id == self.external_id)

        # IDs filter
        if self.ids:
            filters.append(job_model.id.in_(self.ids))

        # Salary filters
        if self.salary_min_gte is not None:
            filters.append(job_model.salary_min >= self.salary_min_gte)

        if self.salary_max_lte is not None:
            filters.append(job_model.salary_max <= self.salary_max_lte)

        return filters

    def apply_to_query(self, query: Query, job_model) -> Query:
        """
        Apply search filters to a SQLAlchemy query.

        Args:
            query: Base SQLAlchemy query
            job_model: The Job SQLAlchemy model class

        Returns:
            Filtered query
        """
        filters = self.build_filters(job_model)

        if filters:
            query = query.filter(and_(*filters))

        return query
