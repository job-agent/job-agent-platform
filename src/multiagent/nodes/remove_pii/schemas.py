"""Pydantic schemas for remove_pii node."""

from pydantic import BaseModel, Field


class ProfessionalInfo(BaseModel):
    """Schema for extracted professional information from CV.

    Attributes:
        professional_content: All professional information from CV with PII removed
    """
    professional_content: str = Field(
        description="All professional information extracted from the CV, including skills, experience, education, and qualifications. All personally identifiable information has been removed or generalized."
    )
