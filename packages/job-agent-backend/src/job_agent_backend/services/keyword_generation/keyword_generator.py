"""Keyword generator service for extracting keywords from essay content."""

import logging
from typing import List, Optional

from job_agent_backend.contracts import IModelFactory
from job_agent_platform_contracts.essay_repository import IEssayRepository

from job_agent_backend.services.keyword_generation.schemas import KeywordsExtraction
from job_agent_backend.services.keyword_generation.prompts import KEYWORD_EXTRACTION_PROMPT


logger = logging.getLogger(__name__)

MAX_KEYWORDS = 10


class KeywordGenerator:
    """Service for extracting keywords from essay content using an LLM.

    This service analyzes essay question and answer fields to extract
    relevant keywords including hard skills, soft skills, and contextual
    label words.
    """

    def __init__(
        self,
        model_factory: IModelFactory,
        repository: IEssayRepository,
    ):
        """Initialize the keyword generator.

        Args:
            model_factory: Factory for retrieving the keyword extraction model
            repository: Essay repository for persisting keywords
        """
        self._model_factory = model_factory
        self._repository = repository

    def generate_keywords(
        self,
        essay_id: int,
        question: Optional[str],
        answer: Optional[str],
    ) -> List[str]:
        """Generate keywords from essay content.

        Extracts up to 10 keywords from the essay's question and answer fields
        using an LLM. Keywords are normalized (trimmed), deduplicated
        (case-insensitive), and persisted to the repository.

        Args:
            essay_id: ID of the essay to generate keywords for
            question: The essay question (may be None)
            answer: The essay answer (may be None)

        Returns:
            List of extracted keywords (empty list if extraction fails or
            content is empty)
        """
        if self._is_empty_content(question, answer):
            return []

        try:
            raw_keywords = self._extract_keywords(question, answer)
            keywords = self._process_keywords(raw_keywords)

            if keywords:
                self._repository.update_keywords(essay_id, keywords)

            return keywords

        except Exception as e:
            logger.warning(f"Failed to generate keywords for essay {essay_id}: {e}")
            return []

    def _is_empty_content(
        self,
        question: Optional[str],
        answer: Optional[str],
    ) -> bool:
        """Check if both question and answer are empty or whitespace-only.

        Args:
            question: The essay question
            answer: The essay answer

        Returns:
            True if both are empty/whitespace-only, False otherwise
        """
        question_empty = not question or not question.strip()
        answer_empty = not answer or not answer.strip()
        return question_empty and answer_empty

    def _extract_keywords(
        self,
        question: Optional[str],
        answer: Optional[str],
    ) -> List[str]:
        """Extract keywords using the LLM.

        Args:
            question: The essay question
            answer: The essay answer

        Returns:
            List of raw keywords from the LLM
        """
        base_model = self._model_factory.get_model(model_id="keyword-extraction")
        structured_model = base_model.with_structured_output(KeywordsExtraction)

        messages = KEYWORD_EXTRACTION_PROMPT.invoke(
            {
                "question": question or "",
                "answer": answer or "",
            }
        )

        result = structured_model.invoke(messages)

        if not isinstance(result, KeywordsExtraction):
            return []

        return result.keywords or []

    def _process_keywords(self, raw_keywords: List[str]) -> List[str]:
        """Normalize, deduplicate, and limit keywords.

        Args:
            raw_keywords: Keywords from LLM extraction

        Returns:
            Processed list of keywords
        """
        seen_lower: set[str] = set()
        processed: List[str] = []

        for keyword in raw_keywords:
            trimmed = keyword.strip()
            if not trimmed:
                continue

            lower = trimmed.lower()
            if lower in seen_lower:
                continue

            seen_lower.add(lower)
            processed.append(trimmed)

            if len(processed) >= MAX_KEYWORDS:
                break

        return processed
