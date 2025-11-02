"""Job update schema."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class JobUpdate(BaseModel):
    """Schema for updating an existing job."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    company: Optional[str] = Field(None, min_length=1, max_length=300)
    location: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    job_type: Optional[str] = Field(None, max_length=100)
    experience_level: Optional[str] = Field(None, max_length=100)
    salary_min: Optional[float] = Field(None, ge=0)
    salary_max: Optional[float] = Field(None, ge=0)
    salary_currency: Optional[str] = Field(None, max_length=10)
    external_id: Optional[str] = Field(None, max_length=300)
    source: Optional[str] = Field(None, max_length=100)
    source_url: Optional[str] = None
    is_active: Optional[bool] = None
    is_remote: Optional[bool] = None
    posted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    extra_data: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)
