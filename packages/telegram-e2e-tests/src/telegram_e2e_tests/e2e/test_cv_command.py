"""E2E tests for /cv command."""

import pytest

pytestmark = pytest.mark.e2e


class TestCVCommand:
    """E2E tests for the /cv bot command."""

    async def test_cv_command_responds_appropriately(self, telegram_qa_client):
        """Bot should respond to /cv command with CV info or missing CV message.

        Verifies that:
        - The bot is responsive and processes the /cv command
        - The response indicates either CV content or prompts to upload
        - The bot handles both states (CV exists / CV not found) gracefully

        This is an E2E test to verify the CV command is functional.
        """
        response = await telegram_qa_client.send_and_wait("/cv")

        response_lower = response.lower()
        # Accept either "no cv"/"not found" (no CV) or "cv"/"content" (CV exists)
        has_no_cv_message = "no cv" in response_lower or "not found" in response_lower
        has_cv_content = "cv" in response_lower or "content" in response_lower
        assert has_no_cv_message or has_cv_content, (
            f"Expected response about CV status, got: {response[:200]}"
        )
