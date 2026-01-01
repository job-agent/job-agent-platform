"""E2E tests for /add_essay command."""

import pytest

from telegram_e2e_tests.e2e.helpers import extract_essay_id

pytestmark = pytest.mark.e2e


class TestAddEssayCommand:
    """E2E tests for the /add_essay bot command."""

    async def test_add_essay_without_content_shows_instructions(self, telegram_qa_client):
        """Bot should respond with usage instructions when /add_essay is sent without content.

        Verifies that:
        - The bot is responsive and processes the /add_essay command
        - When no content is provided, instructions are shown
        - Instructions explain the required Answer: format

        This is an E2E test to verify the add_essay command shows
        helpful guidance to users.
        """
        response = await telegram_qa_client.send_and_wait("/add_essay")

        response_lower = response.lower()
        assert "answer:" in response_lower, (
            f"Expected response to contain 'Answer:' format instruction, got: {response[:200]}"
        )

    async def test_add_essay_missing_answer_marker_shows_format_error(self, telegram_qa_client):
        """Bot should respond with format error when content lacks 'Answer:' marker.

        Verifies that:
        - The bot validates the essay format
        - Missing Answer: marker produces a clear error
        - The error shows the correct format to use

        This tests input validation for the add_essay command.
        """
        response = await telegram_qa_client.send_and_wait(
            "/add_essay some random text without marker"
        )

        response_lower = response.lower()
        assert "invalid format" in response_lower or "answer:" in response_lower, (
            f"Expected format error or instructions, got: {response[:200]}"
        )

    async def test_add_essay_empty_answer_shows_validation_error(self, telegram_qa_client):
        """Bot should respond with error when Answer: marker has no content.

        Verifies that:
        - The bot validates that the answer is not empty
        - Empty answer produces a clear error message
        - The error specifically mentions the answer being empty

        This tests validation of empty answer content.
        """
        response = await telegram_qa_client.send_and_wait("/add_essay Answer:")

        response_lower = response.lower()
        assert "empty" in response_lower or "cannot be empty" in response_lower, (
            f"Expected error about empty answer, got: {response[:200]}"
        )

    async def test_add_essay_with_valid_answer_only_succeeds(self, telegram_qa_client):
        """Bot should successfully save essay with valid answer-only format.

        Verifies that:
        - The bot accepts valid answer-only format
        - A success message is returned with the essay ID
        - The essay is persisted (ID is assigned)

        This tests the happy path for answer-only essay creation.
        The created essay will be cleaned up in subsequent tests.
        """
        unique_content = "Smoke test essay content for answer-only format validation"
        response = await telegram_qa_client.send_and_wait_final(
            f"/add_essay Answer: {unique_content}",
            timeout_seconds=60,
            stable_seconds=3.0,
        )

        response_lower = response.lower()
        assert "saved" in response_lower or "success" in response_lower, (
            f"Expected success message, got: {response[:200]}"
        )

        essay_id = extract_essay_id(response)
        assert essay_id is not None, f"Expected response to contain essay ID, got: {response[:200]}"

    async def test_add_essay_with_question_and_answer_succeeds(self, telegram_qa_client):
        """Bot should successfully save essay with question and answer format.

        Verifies that:
        - The bot accepts the full question+answer format
        - A success message is returned with the essay ID
        - The essay is persisted correctly

        This tests the happy path for full essay creation.
        """
        question = "What is your experience with smoke testing?"
        answer = "I have extensive experience validating systems via E2E smoke tests"
        response = await telegram_qa_client.send_and_wait_final(
            f"/add_essay Question: {question} Answer: {answer}",
            timeout_seconds=60,
            stable_seconds=3.0,
        )

        response_lower = response.lower()
        assert "saved" in response_lower or "success" in response_lower, (
            f"Expected success message, got: {response[:200]}"
        )

        essay_id = extract_essay_id(response)
        assert essay_id is not None, f"Expected response to contain essay ID, got: {response[:200]}"
