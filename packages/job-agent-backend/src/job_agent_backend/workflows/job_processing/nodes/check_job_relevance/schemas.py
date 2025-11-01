"""Pydantic schemas for check_job_relevance node."""

from pydantic import BaseModel, Field


class JobRelevance(BaseModel):
    """Schema for determining job relevance based on CV.

    Attributes:
        is_relevant: Boolean indicating if the job is relevant to the candidate
    """
    is_relevant: bool = Field(
        description="True if the job is relevant to the candidate's profile, False if clearly irrelevant"
    )
