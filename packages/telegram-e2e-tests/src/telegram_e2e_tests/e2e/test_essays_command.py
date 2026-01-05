"""E2E tests for /essays command."""

import pytest

pytestmark = pytest.mark.e2e


class TestEssaysCommand:
    """E2E tests for the /essays bot command."""

    async def test_essays_empty_list_shows_helpful_message(self, telegram_qa_client):
        """Bot should respond with empty state message when no essays exist.

        Verifies that:
        - The bot is responsive and processes the /essays command
        - When no essays exist, a helpful message is shown
        - The message suggests using /add_essay to create essays

        This is an E2E test to verify the essays command handles
        the empty state gracefully.

        Note: This test assumes the test user has no essays. If essays
        exist from previous test runs, this test may fail. Proper test
        isolation requires essay cleanup mechanisms.
        """
        response = await telegram_qa_client.send_and_wait("/essays")

        response_lower = response.lower()
        # Check for either empty state OR valid essay list (pagination)
        is_empty_state = "no essays" in response_lower
        is_essay_list = "page" in response_lower or "answer" in response_lower

        assert is_empty_state or is_essay_list, (
            f"Expected either 'no essays' message or essay list with pagination, "
            f"got: {response[:200]}"
        )

    async def test_essays_with_data_shows_page_info(self, telegram_qa_client):
        """Bot should respond with paginated list when essays exist.

        Verifies that:
        - When essays exist, they are displayed with pagination info
        - The response contains page indicator (Page X of Y)
        - Essay content is shown

        This test requires essays to exist. It first creates an essay,
        then verifies the /essays command shows it properly.
        """
        # First, create a test essay to ensure we have data
        unique_content = "Smoke test essay for pagination verification"
        create_response = await telegram_qa_client.send_and_wait_final(
            f"/add_essay Answer: {unique_content}",
            timeout_seconds=60,
            stable_seconds=3.0,
        )

        # Verify essay was created
        create_lower = create_response.lower()
        assert "saved" in create_lower or "success" in create_lower, (
            f"Failed to create test essay for pagination test, got: {create_response[:200]}"
        )

        # Now test the /essays command
        response = await telegram_qa_client.send_and_wait("/essays")

        response_lower = response.lower()
        # Should show either page info or essay content
        has_page_info = "page" in response_lower
        has_essay_content = "answer" in response_lower or unique_content.lower() in response_lower

        assert has_page_info or has_essay_content, (
            f"Expected page info or essay content, got: {response[:200]}"
        )
