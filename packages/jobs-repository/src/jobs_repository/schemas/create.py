"""Job creation schema."""

from typing import Optional
from pydantic import Field

from jobs_repository.schemas.base import JobBase


class JobCreate(JobBase):
    """Schema for creating a new job."""

    external_id: Optional[str] = Field(None, max_length=300, description="External job identifier")
    source: Optional[str] = Field(None, max_length=100, description="Job source (e.g., LinkedIn)")
    source_url: Optional[str] = Field(None, description="URL to the original job posting")
