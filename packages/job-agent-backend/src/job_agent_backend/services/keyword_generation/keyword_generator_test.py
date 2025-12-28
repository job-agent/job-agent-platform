"""Tests for KeywordGenerator service.

These tests verify the KeywordGenerator extracts keywords from essay content
using an LLM, handles errors gracefully, and persists results to the repository.
"""

from typing import List
from unittest.mock import MagicMock


# These imports will fail until implementation exists (expected for RED phase)
from job_agent_backend.services.keyword_generation import KeywordGenerator
from job_agent_backend.services.keyword_generation.schemas import KeywordsExtraction


def _create_mock_model(keywords: List[str]) -> MagicMock:
    """Create a mock model that returns a KeywordsExtraction with the given keywords."""
    mock_model = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = KeywordsExtraction(keywords=keywords)
    mock_model.with_structured_output.return_value = mock_structured
    return mock_model


def _create_mock_factory(mock_model: MagicMock) -> MagicMock:
    """Create a mock model factory that returns the given model."""
    mock_factory = MagicMock()
    mock_factory.get_model.return_value = mock_model
    return mock_factory


def _create_mock_repository(update_returns: bool = True) -> MagicMock:
    """Create a mock essay repository."""
    mock_repository = MagicMock()
    mock_repository.update_keywords.return_value = update_returns
    return mock_repository


class TestKeywordGeneratorEmptyContent:
    """Tests for handling empty or whitespace-only content."""

    def test_returns_empty_list_when_both_question_and_answer_are_none(self):
        """Generator returns empty list when both question and answer are None."""
        mock_factory = MagicMock()
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        result = generator.generate_keywords(
            essay_id=1,
            question=None,
            answer=None,
        )

        assert result == []
        mock_factory.get_model.assert_not_called()
        mock_repository.update_keywords.assert_not_called()

    def test_returns_empty_list_when_both_question_and_answer_are_empty(self):
        """Generator returns empty list when both question and answer are empty strings."""
        mock_factory = MagicMock()
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        result = generator.generate_keywords(
            essay_id=1,
            question="",
            answer="",
        )

        assert result == []
        mock_factory.get_model.assert_not_called()

    def test_returns_empty_list_when_content_is_whitespace_only(self):
        """Generator returns empty list when question and answer contain only whitespace."""
        mock_factory = MagicMock()
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        result = generator.generate_keywords(
            essay_id=1,
            question="   \n\t  ",
            answer="  \t\n  ",
        )

        assert result == []
        mock_factory.get_model.assert_not_called()

    def test_extracts_keywords_when_only_answer_has_content(self):
        """Generator extracts keywords when question is None but answer has content."""
        expected_keywords = ["Python", "Django"]
        mock_model = _create_mock_model(expected_keywords)
        mock_factory = _create_mock_factory(mock_model)
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        result = generator.generate_keywords(
            essay_id=1,
            question=None,
            answer="I have experience with Python and Django.",
        )

        assert result == expected_keywords
        mock_factory.get_model.assert_called_once_with(model_id="keyword-extraction")

    def test_extracts_keywords_when_only_question_has_content(self):
        """Generator extracts keywords when answer is empty but question has content."""
        expected_keywords = ["leadership", "teamwork"]
        mock_model = _create_mock_model(expected_keywords)
        mock_factory = _create_mock_factory(mock_model)
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        result = generator.generate_keywords(
            essay_id=1,
            question="Describe your leadership and teamwork experience.",
            answer="",
        )

        assert result == expected_keywords


class TestKeywordGeneratorExtraction:
    """Tests for successful keyword extraction."""

    def test_extracts_keywords_from_question_and_answer(self):
        """Generator extracts keywords from both question and answer content."""
        expected_keywords = ["Python", "leadership", "AWS", "communication"]
        mock_model = _create_mock_model(expected_keywords)
        mock_factory = _create_mock_factory(mock_model)
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        result = generator.generate_keywords(
            essay_id=1,
            question="What are your key technical skills?",
            answer="I have Python, AWS experience and strong communication skills.",
        )

        assert result == expected_keywords

    def test_persists_keywords_to_repository(self):
        """Generator calls repository.update_keywords with extracted keywords."""
        expected_keywords = ["Python", "Django", "PostgreSQL"]
        mock_model = _create_mock_model(expected_keywords)
        mock_factory = _create_mock_factory(mock_model)
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        generator.generate_keywords(
            essay_id=42,
            question="Technical skills?",
            answer="Python, Django, PostgreSQL",
        )

        mock_repository.update_keywords.assert_called_once_with(42, expected_keywords)

    def test_uses_keyword_extraction_model(self):
        """Generator uses the 'keyword-extraction' model ID."""
        mock_model = _create_mock_model(["skill"])
        mock_factory = _create_mock_factory(mock_model)
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        generator.generate_keywords(
            essay_id=1,
            question="Question",
            answer="Answer with skill",
        )

        mock_factory.get_model.assert_called_once_with(model_id="keyword-extraction")


class TestKeywordGeneratorLimit:
    """Tests for keyword limit enforcement."""

    def test_limits_keywords_to_ten(self):
        """Generator returns at most 10 keywords when LLM returns more."""
        many_keywords = [f"keyword{i}" for i in range(15)]
        mock_model = _create_mock_model(many_keywords)
        mock_factory = _create_mock_factory(mock_model)
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        result = generator.generate_keywords(
            essay_id=1,
            question="Question",
            answer="Answer with many skills",
        )

        assert len(result) == 10
        # Should keep the first 10 (most relevant as ordered by LLM)
        assert result == many_keywords[:10]

    def test_persists_only_ten_keywords_to_repository(self):
        """Generator persists only the first 10 keywords to repository."""
        many_keywords = [f"keyword{i}" for i in range(15)]
        mock_model = _create_mock_model(many_keywords)
        mock_factory = _create_mock_factory(mock_model)
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        generator.generate_keywords(
            essay_id=1,
            question="Question",
            answer="Answer",
        )

        mock_repository.update_keywords.assert_called_once_with(1, many_keywords[:10])

    def test_returns_all_keywords_when_fewer_than_ten(self):
        """Generator returns all keywords when LLM returns fewer than 10."""
        few_keywords = ["Python", "Django", "SQL"]
        mock_model = _create_mock_model(few_keywords)
        mock_factory = _create_mock_factory(mock_model)
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        result = generator.generate_keywords(
            essay_id=1,
            question="Question",
            answer="Answer",
        )

        assert result == few_keywords
        assert len(result) == 3


class TestKeywordGeneratorDeduplication:
    """Tests for keyword deduplication."""

    def test_removes_duplicate_keywords_case_insensitive(self):
        """Generator removes duplicates with case-insensitive comparison."""
        keywords_with_duplicates = ["Python", "python", "PYTHON", "Django", "django"]
        mock_model = _create_mock_model(keywords_with_duplicates)
        mock_factory = _create_mock_factory(mock_model)
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        result = generator.generate_keywords(
            essay_id=1,
            question="Question",
            answer="Answer",
        )

        # Should keep first occurrence
        assert len(result) == 2
        assert result[0].lower() == "python"
        assert result[1].lower() == "django"

    def test_preserves_first_occurrence_casing(self):
        """Generator preserves the casing of the first occurrence."""
        keywords = ["Python", "python", "JavaScript", "JAVASCRIPT"]
        mock_model = _create_mock_model(keywords)
        mock_factory = _create_mock_factory(mock_model)
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        result = generator.generate_keywords(
            essay_id=1,
            question="Question",
            answer="Answer",
        )

        assert result == ["Python", "JavaScript"]


class TestKeywordGeneratorNormalization:
    """Tests for keyword normalization."""

    def test_trims_whitespace_from_keywords(self):
        """Generator trims leading and trailing whitespace from keywords."""
        keywords_with_whitespace = ["  Python  ", "\tDjango\n", " SQL "]
        mock_model = _create_mock_model(keywords_with_whitespace)
        mock_factory = _create_mock_factory(mock_model)
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        result = generator.generate_keywords(
            essay_id=1,
            question="Question",
            answer="Answer",
        )

        assert result == ["Python", "Django", "SQL"]

    def test_removes_empty_strings_after_trim(self):
        """Generator removes keywords that become empty after trimming."""
        keywords_with_empty = ["Python", "   ", "", "\t\n", "Django"]
        mock_model = _create_mock_model(keywords_with_empty)
        mock_factory = _create_mock_factory(mock_model)
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        result = generator.generate_keywords(
            essay_id=1,
            question="Question",
            answer="Answer",
        )

        assert result == ["Python", "Django"]

    def test_normalization_before_deduplication(self):
        """Generator normalizes keywords before checking for duplicates."""
        keywords = ["  Python  ", "Python", "python  "]
        mock_model = _create_mock_model(keywords)
        mock_factory = _create_mock_factory(mock_model)
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        result = generator.generate_keywords(
            essay_id=1,
            question="Question",
            answer="Answer",
        )

        assert result == ["Python"]


class TestKeywordGeneratorErrorHandling:
    """Tests for error handling."""

    def test_returns_empty_list_on_model_factory_exception(self):
        """Generator returns empty list when model factory raises exception."""
        mock_factory = MagicMock()
        mock_factory.get_model.side_effect = Exception("Model unavailable")
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        result = generator.generate_keywords(
            essay_id=1,
            question="Question",
            answer="Answer with content",
        )

        assert result == []
        mock_repository.update_keywords.assert_not_called()

    def test_returns_empty_list_on_model_invocation_exception(self):
        """Generator returns empty list when model invocation raises exception."""
        mock_model = MagicMock()
        mock_structured = MagicMock()
        mock_structured.invoke.side_effect = Exception("LLM timeout")
        mock_model.with_structured_output.return_value = mock_structured
        mock_factory = _create_mock_factory(mock_model)
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        result = generator.generate_keywords(
            essay_id=1,
            question="Question",
            answer="Answer",
        )

        assert result == []
        mock_repository.update_keywords.assert_not_called()

    def test_does_not_propagate_model_exception(self):
        """Generator catches model exceptions and does not propagate them."""
        mock_factory = MagicMock()
        mock_factory.get_model.side_effect = RuntimeError("Unexpected error")
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        # Should not raise
        result = generator.generate_keywords(
            essay_id=1,
            question="Question",
            answer="Answer",
        )

        assert result == []

    def test_returns_empty_list_on_repository_exception(self):
        """Generator returns empty list when repository update raises exception."""
        expected_keywords = ["Python", "Django"]
        mock_model = _create_mock_model(expected_keywords)
        mock_factory = _create_mock_factory(mock_model)
        mock_repository = MagicMock()
        mock_repository.update_keywords.side_effect = Exception("DB connection failed")
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        result = generator.generate_keywords(
            essay_id=1,
            question="Question",
            answer="Answer",
        )

        assert result == []

    def test_does_not_propagate_repository_exception(self):
        """Generator catches repository exceptions and does not propagate them."""
        mock_model = _create_mock_model(["Python"])
        mock_factory = _create_mock_factory(mock_model)
        mock_repository = MagicMock()
        mock_repository.update_keywords.side_effect = RuntimeError("Unexpected DB error")
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        # Should not raise
        result = generator.generate_keywords(
            essay_id=1,
            question="Question",
            answer="Answer",
        )

        assert result == []

    def test_handles_result_without_keywords_attribute(self):
        """Generator handles model result that lacks keywords attribute."""
        mock_model = MagicMock()
        mock_structured = MagicMock()
        mock_result = MagicMock(spec=[])  # Object with no attributes
        mock_structured.invoke.return_value = mock_result
        mock_model.with_structured_output.return_value = mock_structured
        mock_factory = _create_mock_factory(mock_model)
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        result = generator.generate_keywords(
            essay_id=1,
            question="Question",
            answer="Answer",
        )

        assert result == []

    def test_handles_result_with_none_keywords(self):
        """Generator handles model result where keywords is None."""
        mock_model = MagicMock()
        mock_structured = MagicMock()
        mock_result = MagicMock()
        mock_result.keywords = None
        mock_structured.invoke.return_value = mock_result
        mock_model.with_structured_output.return_value = mock_structured
        mock_factory = _create_mock_factory(mock_model)
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        result = generator.generate_keywords(
            essay_id=1,
            question="Question",
            answer="Answer",
        )

        assert result == []


class TestKeywordGeneratorDoesNotPersistEmptyResults:
    """Tests verifying repository is not called for empty results."""

    def test_does_not_call_repository_when_no_keywords_extracted(self):
        """Generator does not call repository when LLM returns empty list."""
        mock_model = _create_mock_model([])
        mock_factory = _create_mock_factory(mock_model)
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        result = generator.generate_keywords(
            essay_id=1,
            question="Question",
            answer="Answer",
        )

        assert result == []
        mock_repository.update_keywords.assert_not_called()

    def test_does_not_call_repository_when_all_keywords_are_empty_strings(self):
        """Generator does not call repository when all keywords are empty after normalization."""
        mock_model = _create_mock_model(["   ", "", "\t\n"])
        mock_factory = _create_mock_factory(mock_model)
        mock_repository = _create_mock_repository()
        generator = KeywordGenerator(
            model_factory=mock_factory,
            repository=mock_repository,
        )

        result = generator.generate_keywords(
            essay_id=1,
            question="Question",
            answer="Answer",
        )

        assert result == []
        mock_repository.update_keywords.assert_not_called()
