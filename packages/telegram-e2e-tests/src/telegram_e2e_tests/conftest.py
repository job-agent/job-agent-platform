"""Pytest fixtures for telegram-qa-service tests."""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Load .env file from package root if it exists
# conftest.py is at: src/telegram_e2e_tests/conftest.py
# .env is at: .env (package root)
# So we need to go up 3 levels: telegram_e2e_tests/ -> src/ -> telegram-qa-service/
_env_path = Path(__file__).parent.parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)


@pytest.fixture(scope="session")
def skip_if_no_credentials():
    """Skip tests if Telegram QA credentials are not configured.

    This fixture checks for required environment variables and skips
    the test with a descriptive message if they are not set.
    """
    if not os.getenv("TELEGRAM_API_ID"):
        pytest.skip("Telegram QA credentials not configured")


@pytest.fixture
async def telegram_qa_client(skip_if_no_credentials):
    """Create a connected TelegramQAClient for E2E tests.

    This fixture is session-scoped for efficiency - it reuses the same
    Telegram connection across all E2E tests in a session.

    The fixture:
    1. Skips if credentials are not configured
    2. Creates and connects the client
    3. Yields the connected client for test use
    4. Disconnects after all tests complete

    Usage:
        @pytest.mark.e2e
        async def test_bot_responds(telegram_qa_client):
            response = await telegram_qa_client.send_and_wait("/start")
            assert "Welcome" in response
    """
    from telegram_e2e_tests.client import TelegramQAClient

    client = TelegramQAClient()
    async with client:
        yield client
