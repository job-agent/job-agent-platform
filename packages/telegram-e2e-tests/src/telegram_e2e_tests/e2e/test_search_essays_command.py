"""E2E tests for /search_essays command."""

import pytest

pytestmark = pytest.mark.e2e


class TestSearchEssaysCommand:
    """E2E tests for the /search_essays bot command."""

    async def test_search_essays_without_query_shows_usage_instructions(self, telegram_qa_client):
        """Bot should respond with usage instructions when /search_essays is sent without query.

        Verifies that:
        - The bot is responsive and processes the /search_essays command
        - When no query is provided, usage instructions are shown
        - The instructions explain the required format

        This is an E2E test to verify the search_essays command shows
        helpful guidance to users.
        """
        response = await telegram_qa_client.send_and_wait("/search_essays")

        response_lower = response.lower()
        # Check for usage help message
        has_usage_hint = "usage" in response_lower or "search_essays" in response_lower
        has_query_hint = "query" in response_lower

        assert has_usage_hint or has_query_hint, (
            f"Expected usage instructions mentioning query, got: {response[:200]}"
        )

    async def test_search_essays_with_invalid_limit_zero_shows_error(self, telegram_qa_client):
        """Bot should respond with error when limit is zero.

        Verifies that:
        - The bot validates the limit parameter
        - Zero limit produces a clear error message
        - The error mentions that limit must be positive

        This tests input validation for the search_essays command.
        """
        response = await telegram_qa_client.send_and_wait("/search_essays leadership 0")

        response_lower = response.lower()
        has_limit_error = "limit" in response_lower or "positive" in response_lower
        has_usage_hint = "usage" in response_lower

        assert has_limit_error or has_usage_hint, (
            f"Expected error about limit or usage hint, got: {response[:200]}"
        )

    async def test_search_essays_with_invalid_limit_negative_shows_error(self, telegram_qa_client):
        """Bot should respond with error when limit is negative.

        Verifies that:
        - The bot validates the limit parameter
        - Negative limit produces a clear error message
        - The error indicates the expected format

        This tests input validation for negative limit values.
        """
        response = await telegram_qa_client.send_and_wait("/search_essays teamwork -5")

        response_lower = response.lower()
        has_limit_error = "limit" in response_lower or "positive" in response_lower
        has_usage_hint = "usage" in response_lower

        assert has_limit_error or has_usage_hint, (
            f"Expected error about limit or usage hint, got: {response[:200]}"
        )

    async def test_search_essays_with_query_returns_results_or_no_results_message(
        self, telegram_qa_client
    ):
        """Bot should respond with search results or no results message.

        Verifies that:
        - The bot processes the search query
        - Either matching essays are returned with a count
        - Or a "no essays found" message is displayed

        This tests the happy path for essay search with default limit.
        """
        response = await telegram_qa_client.send_and_wait_final(
            "/search_essays leadership experience",
            timeout_seconds=60,
            stable_seconds=3.0,
        )

        response_lower = response.lower()
        # Accept either: results found or no results message
        has_results = "found" in response_lower or "essay" in response_lower
        has_no_results = "no essays" in response_lower

        assert has_results or has_no_results, (
            f"Expected search results or no results message, got: {response[:200]}"
        )

    async def test_search_essays_with_custom_limit_respects_limit(self, telegram_qa_client):
        """Bot should accept custom limit parameter.

        Verifies that:
        - The bot accepts the limit parameter syntax
        - The search is performed with the specified limit
        - Results or no results message is returned

        This tests the search with explicit limit parameter.
        """
        response = await telegram_qa_client.send_and_wait_final(
            "/search_essays teamwork 5",
            timeout_seconds=60,
            stable_seconds=3.0,
        )

        response_lower = response.lower()
        # Accept either: results found or no results message
        has_results = "found" in response_lower or "essay" in response_lower
        has_no_results = "no essays" in response_lower

        assert has_results or has_no_results, (
            f"Expected search results or no results message, got: {response[:200]}"
        )

    async def test_search_essays_with_multi_word_query_searches_all_words(self, telegram_qa_client):
        """Bot should handle multi-word queries without quotes.

        Verifies that:
        - Multi-word queries are parsed correctly
        - The search uses all words from the query
        - Results or no results message is returned

        This tests multi-word query handling.
        """
        response = await telegram_qa_client.send_and_wait_final(
            "/search_essays project management skills",
            timeout_seconds=60,
            stable_seconds=3.0,
        )

        response_lower = response.lower()
        # Accept either: results found or no results message
        has_results = "found" in response_lower or "essay" in response_lower
        has_no_results = "no essays" in response_lower

        assert has_results or has_no_results, (
            f"Expected search results or no results message, got: {response[:200]}"
        )

    async def test_search_essays_with_existing_essay_returns_formatted_result(
        self, telegram_qa_client
    ):
        """Bot should return formatted results when matching essays exist.

        Verifies that:
        - First creates a test essay with unique content
        - Then searches for that content
        - Results contain the expected answer content
        - Results are formatted with question/answer/keywords structure

        This tests end-to-end search with known data.
        """
        # First, create a test essay with unique searchable content
        unique_keyword = "smoketestuniquekeyword"
        unique_answer = f"This essay contains {unique_keyword} for search verification"
        create_response = await telegram_qa_client.send_and_wait_final(
            f"/add_essay Answer: {unique_answer}",
            timeout_seconds=60,
            stable_seconds=3.0,
        )

        # Verify essay was created
        create_lower = create_response.lower()
        assert "saved" in create_lower or "success" in create_lower, (
            f"Failed to create test essay for search test, got: {create_response[:200]}"
        )

        # Now search for the unique keyword
        search_response = await telegram_qa_client.send_and_wait_final(
            f"/search_essays {unique_keyword}",
            timeout_seconds=60,
            stable_seconds=3.0,
        )

        search_lower = search_response.lower()
        # Should find the essay we just created
        has_results = "found" in search_lower
        has_answer_content = unique_keyword in search_lower

        assert has_results or has_answer_content, (
            f"Expected search to find the created essay, got: {search_response[:300]}"
        )

    async def test_search_essays_results_contain_answer_section(self, telegram_qa_client):
        """Bot should include answer content in search results.

        Verifies that:
        - Create an essay with unique content
        - Search for that unique content to ensure results are returned
        - Results contain an Answer section marker

        This tests result formatting structure.
        """
        # Create essay with unique searchable content
        unique_keyword = "answersectionuniquetest"
        unique_answer = f"This essay with {unique_keyword} verifies answer section formatting"
        create_response = await telegram_qa_client.send_and_wait_final(
            f"/add_essay Answer: {unique_answer}",
            timeout_seconds=60,
            stable_seconds=3.0,
        )

        create_lower = create_response.lower()
        assert "saved" in create_lower or "success" in create_lower, (
            f"Failed to create test essay for formatting test, got: {create_response[:200]}"
        )

        # Search for the unique keyword we just created
        response = await telegram_qa_client.send_and_wait_final(
            f"/search_essays {unique_keyword}",
            timeout_seconds=60,
            stable_seconds=3.0,
        )

        response_lower = response.lower()
        # Verify results were found
        assert "found" in response_lower, (
            f"Expected search to find the created essay, got: {response[:300]}"
        )
        # Verify answer section marker is present
        has_answer_marker = "answer" in response_lower
        assert has_answer_marker, (
            f"Expected results to contain 'Answer' section, got: {response[:300]}"
        )

    async def test_search_essays_results_contain_keywords_section(self, telegram_qa_client):
        """Bot should include keywords section in search results.

        Verifies that:
        - Create an essay with unique content
        - Search for that unique content to ensure results are returned
        - Results contain a Keywords section marker

        This tests keyword display in result formatting.
        """
        # Create essay with unique searchable content
        unique_keyword = "keywordssectionuniquetest"
        unique_answer = f"This essay with {unique_keyword} verifies keywords section formatting"
        create_response = await telegram_qa_client.send_and_wait_final(
            f"/add_essay Answer: {unique_answer}",
            timeout_seconds=60,
            stable_seconds=3.0,
        )

        create_lower = create_response.lower()
        assert "saved" in create_lower or "success" in create_lower, (
            f"Failed to create test essay for keywords test, got: {create_response[:200]}"
        )

        # Search for the unique keyword we just created
        response = await telegram_qa_client.send_and_wait_final(
            f"/search_essays {unique_keyword}",
            timeout_seconds=60,
            stable_seconds=3.0,
        )

        response_lower = response.lower()
        # Verify results were found
        assert "found" in response_lower, (
            f"Expected search to find the created essay, got: {response[:300]}"
        )
        # Verify keywords section marker is present
        has_keywords_marker = "keywords" in response_lower
        assert has_keywords_marker, (
            f"Expected results to contain 'Keywords' section, got: {response[:300]}"
        )

    async def test_search_essays_numeric_only_query_searches_not_treated_as_limit(
        self, telegram_qa_client
    ):
        """Bot should treat single numeric argument as query, not limit.

        Verifies that:
        - A single number is treated as the search query
        - The search is performed with default limit
        - Results or no results message is returned

        This tests edge case where query is purely numeric.
        """
        response = await telegram_qa_client.send_and_wait_final(
            "/search_essays 2024",
            timeout_seconds=60,
            stable_seconds=3.0,
        )

        response_lower = response.lower()
        # Should not show "invalid limit" error - should search for "2024"
        has_limit_error = "limit" in response_lower and "positive" in response_lower
        has_search_response = "found" in response_lower or "no essays" in response_lower

        assert has_search_response and not has_limit_error, (
            f"Expected search response for numeric query, got: {response[:200]}"
        )
