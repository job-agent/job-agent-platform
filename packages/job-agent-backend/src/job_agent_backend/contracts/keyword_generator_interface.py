"""Keyword generator interface definitions."""

from typing import List, Optional, Protocol


class IKeywordGenerator(Protocol):
    """Interface for components that generate keywords from essay content."""

    def generate_keywords(
        self,
        essay_id: int,
        question: Optional[str],
        answer: Optional[str],
    ) -> List[str]:
        """Generate keywords from essay content.

        Args:
            essay_id: ID of the essay to generate keywords for
            question: The essay question (may be None)
            answer: The essay answer (may be None)

        Returns:
            List of extracted keywords (empty list if extraction fails or
            content is empty)
        """
        ...
