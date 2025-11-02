"""Job response schema."""

from datetime import datetime
from typing import Optional
from pydantic import ConfigDict

from jobs_repository.schemas.base import JobBase


class JobResponse(JobBase):
    """Schema for job response with all fields including ID and timestamps."""

    id: int
    external_id: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
