# Telegram QA Service

End-to-end testing service for the Job Agent Telegram bot using Telethon.

## Overview

This package provides a QA client that communicates with the Telegram bot as a real user, enabling automated E2E smoke tests. It uses the Telethon library to interact with the Telegram API.

## Installation

```bash
cd packages/telegram-qa-service
pip install -e .[dev]
```

Or use the root `reinstall_packages.sh` script:

```bash
./scripts/reinstall_packages.sh
```

## Configuration

### Getting Telegram API Credentials

1. Go to https://my.telegram.org
2. Log in with your phone number
3. Go to "API development tools"
4. Create a new application
5. Copy the `api_id` and `api_hash`

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_API_ID` | Yes | - | Your Telegram API ID |
| `TELEGRAM_API_HASH` | Yes | - | Your Telegram API hash |
| `TELEGRAM_QA_BOT_USERNAME` | Yes | - | Bot username to test (e.g., `@job_agent_bot`) |
| `TELEGRAM_QA_SESSION_PATH` | No | `telegram_qa.session` | Path to session file |
| `TELEGRAM_QA_TIMEOUT` | No | `30` | Response timeout in seconds |

### First-Time Authentication

On first run, Telethon will prompt for your phone number and a verification code sent via Telegram. This creates a session file that persists your login.

## Usage

### Using the Client Programmatically

```python
import asyncio
from telegram_qa_service import TelegramQAClient

async def main():
    async with TelegramQAClient() as client:
        # Send a command and wait for response
        response = await client.send_and_wait("/start")
        print(f"Bot response: {response}")

asyncio.run(main())
```

## Architecture

```
telegram-qa-service/
├── src/telegram_qa_service/
│   ├── __init__.py         # Public exports
│   ├── client.py           # TelegramQAClient implementation
│   ├── client_test.py      # Unit tests (co-located)
│   ├── config.py           # Configuration loading
│   ├── config_test.py      # Unit tests (co-located)
│   ├── exceptions.py       # Custom exceptions
│   ├── exceptions_test.py  # Unit tests (co-located)
│   ├── conftest.py         # Shared pytest fixtures
│   └── smoke_tests/        # E2E test scenarios
│       ├── test_start_command.py
│       └── test_help_command.py
├── pyproject.toml
├── .env.example
└── README.md
```

## Requirements

- Python 3.9+
- Telethon
- pytest (for testing)
- A real Telegram user account (not a bot account)
- The target bot must be running and accessible

## Testing

### Test Structure

Tests are co-located with production code following the `*_test.py` naming convention:

```
src/telegram_qa_service/
├── client.py              # Production code
├── client_test.py         # Unit tests for client
├── config.py              # Production code
├── config_test.py         # Unit tests for config
├── exceptions.py          # Production code
├── exceptions_test.py     # Unit tests for exceptions
├── conftest.py            # Shared pytest fixtures
└── smoke_tests/           # E2E smoke tests
    ├── test_start_command.py
    └── test_help_command.py
```

### Test Categories

- **Unit tests** (40 tests): Test configuration loading, error handling, and client behavior with mocked Telethon. No credentials required.
- **E2E tests** (2 tests): Marked with `@pytest.mark.e2e`, require actual bot running and credentials configured.

### Fixtures

Shared fixtures are defined in `src/telegram_qa_service/conftest.py`:

| Fixture | Scope | Description |
|---------|-------|-------------|
| `skip_if_no_credentials` | session | Skips test if `TELEGRAM_API_ID` not set |
| `telegram_qa_client` | function | Connected `TelegramQAClient` for E2E tests |

### Running Tests

```bash
# All tests (unit + E2E)
pytest packages/telegram-qa-service

# Unit tests only (no credentials required)
pytest packages/telegram-qa-service -m "not e2e"

# E2E tests only (requires credentials and running bot)
pytest packages/telegram-qa-service -m e2e

# Verbose output
pytest packages/telegram-qa-service -v
```

E2E tests are skipped automatically if `TELEGRAM_API_ID` is not configured.

### Test Conventions

This package follows the repository-wide testing guidelines from `CLAUDE.md`:

- Tests focus on **observable behavior**, not implementation details
- External systems (Telethon/Telegram) are mocked in unit tests
- No logging assertion tests or trivial dataclass storage tests
- Exception tests verify messages and inheritance for catch-all handling
