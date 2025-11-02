"""Base job schema."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict


class JobBase(BaseModel):
    """Base job schema with common fields."""

    title: str = Field(..., min_length=1, max_length=500, description="Job title")
    company: str = Field(..., min_length=1, max_length=300, description="Company name")
    location: Optional[str] = Field(None, max_length=300, description="Job location")
    description: Optional[str] = Field(None, description="Job description")
    job_type: Optional[str] = Field(
        None, max_length=100, description="Type of job (e.g., Full-time)"
    )
    experience_level: Optional[str] = Field(
        None, max_length=100, description="Required experience level"
    )
    salary_min: Optional[float] = Field(None, ge=0, description="Minimum salary")
    salary_max: Optional[float] = Field(None, ge=0, description="Maximum salary")
    salary_currency: Optional[str] = Field(None, max_length=10, description="Salary currency code")
    is_active: bool = Field(True, description="Whether the job is active")
    is_remote: bool = Field(False, description="Whether the job is remote")
    posted_at: Optional[datetime] = Field(None, description="When the job was posted")
    expires_at: Optional[datetime] = Field(None, description="When the job posting expires")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    @field_validator("salary_max")
    @classmethod
    def validate_salary_range(cls, v: Optional[float], info) -> Optional[float]:
        """Validate that salary_max is greater than salary_min."""
        if v is not None and info.data.get("salary_min") is not None:
            if v < info.data["salary_min"]:
                raise ValueError("salary_max must be greater than or equal to salary_min")
        return v

    model_config = ConfigDict(from_attributes=True)
