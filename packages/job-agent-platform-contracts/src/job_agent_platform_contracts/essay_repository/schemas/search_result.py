"""Essay search result schema."""

from typing import Optional

from pydantic import BaseModel

from job_agent_platform_contracts.essay_repository.schemas.essay import Essay


class EssaySearchResult(BaseModel):
    """Result from hybrid essay search.

    This schema represents a single search result with the matched essay,
    combined score, and optional ranking information from each search method.
    """

    essay: Essay
    score: float
    vector_rank: Optional[int] = None
    text_rank: Optional[int] = None
