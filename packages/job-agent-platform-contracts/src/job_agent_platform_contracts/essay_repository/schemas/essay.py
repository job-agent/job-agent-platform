"""Essay response schema."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class Essay(BaseModel):
    """Response schema representing an essay entity.

    This Pydantic model is used for API responses and data transfer.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    question: Optional[str] = None
    answer: str
    keywords: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
