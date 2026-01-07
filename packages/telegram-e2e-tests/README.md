# Telegram E2E Tests

End-to-end testing service for the Job Agent Telegram bot using Telethon.

## Overview

This package provides a E2E client that communicates with the Telegram bot as a real user, enabling automated E2E tests. It uses the Telethon library to interact with the Telegram API.

## Installation

```bash
cd packages/telegram-e2e-tests
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
from telegram_e2e_tests import TelegramQAClient

async def main():
    async with TelegramQAClient() as client:
        # Send a command and wait for response
        response = await client.send_and_wait("/start")
        print(f"Bot response: {response}")

asyncio.run(main())
```

## Architecture

```
telegram-e2e-tests/
├── src/telegram_e2e_tests/
│   ├── __init__.py         # Public exports
│   ├── client.py           # TelegramQAClient implementation
│   ├── client_test.py      # Unit tests (co-located)
│   ├── config.py           # Configuration loading
│   ├── config_test.py      # Unit tests (co-located)
│   ├── exceptions.py       # Custom exceptions
│   ├── exceptions_test.py  # Unit tests (co-located)
│   ├── conftest.py         # Shared pytest fixtures
│   └── e2e/        # E2E test scenarios
│       ├── helpers.py              # Test utilities (essay ID extraction)
│       ├── helpers_test.py         # Unit tests for helpers
│       ├── test_start_command.py   # /start command
│       ├── test_help_command.py    # /help command
│       ├── test_status_command.py  # /status command
│       ├── test_cancel_command.py  # /cancel command
│       ├── test_cv_command.py      # /cv command
│       ├── test_search_command.py  # /search command
│       ├── test_add_essay_command.py  # /add_essay command
│       ├── test_essays_command.py  # /essays command
│       └── test_search_essays_command.py  # /search_essays command
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
src/telegram_e2e_tests/
├── client.py              # Production code
├── client_test.py         # Unit tests for client
├── config.py              # Production code
├── config_test.py         # Unit tests for config
├── exceptions.py          # Production code
├── exceptions_test.py     # Unit tests for exceptions
├── conftest.py            # Shared pytest fixtures
└── e2e/           # E2E tests
    ├── helpers.py              # Test utilities
    ├── helpers_test.py         # Unit tests for helpers
    ├── test_start_command.py   # /start command
    ├── test_help_command.py    # /help command
    ├── test_status_command.py  # /status command
    ├── test_cancel_command.py  # /cancel command
    ├── test_cv_command.py      # /cv command
    ├── test_search_command.py  # /search command
    ├── test_add_essay_command.py  # /add_essay command
    ├── test_essays_command.py  # /essays command
    └── test_search_essays_command.py  # /search_essays command
```

### Test Categories

- **Unit tests** (43 tests): Test configuration loading, error handling, client behavior with mocked Telethon, and helper utilities. No credentials required.
- **E2E tests** (26 tests): Marked with `@pytest.mark.e2e`, require actual bot running and credentials configured. Cover all 9 bot commands: `/start`, `/help`, `/status`, `/cancel`, `/cv`, `/search`, `/add_essay`, `/essays`, `/search_essays`.

### Fixtures

Shared fixtures are defined in `src/telegram_e2e_tests/conftest.py`:

| Fixture | Scope | Description |
|---------|-------|-------------|
| `skip_if_no_credentials` | session | Skips test if `TELEGRAM_API_ID` not set |
| `telegram_qa_client` | function | Connected `TelegramQAClient` for E2E tests |

### Running Tests

```bash
# All tests (unit + E2E)
pytest packages/telegram-e2e-tests

# Unit tests only (no credentials required)
pytest packages/telegram-e2e-tests -m "not e2e"

# E2E tests only (requires credentials and running bot)
pytest packages/telegram-e2e-tests -m e2e

# Verbose output
pytest packages/telegram-e2e-tests -v
```

E2E tests are skipped automatically if `TELEGRAM_API_ID` is not configured.

### E2E Test Coverage

The E2E tests verify bot command responses:

| Command | Test File | Scenarios |
|---------|-----------|-----------|
| `/start` | `test_start_command.py` | Welcome message response |
| `/help` | `test_help_command.py` | Lists all available commands |
| `/status` | `test_status_command.py` | "No active searches" when idle |
| `/cancel` | `test_cancel_command.py` | "No active search to cancel" when idle |
| `/cv` | `test_cv_command.py` | "No CV found" when not uploaded |
| `/search` | `test_search_command.py` | CV prerequisite error, invalid parameters, deprecated parameters |
| `/add_essay` | `test_add_essay_command.py` | Instructions, format errors, empty answer, successful creation |
| `/essays` | `test_essays_command.py` | Empty list message, pagination with data |
| `/search_essays` | `test_search_essays_command.py` | Usage instructions, invalid limit (zero, negative), valid query, custom limit, multi-word query, result formatting (Answer, Keywords sections), numeric-only query |

Tests use case-insensitive keyword matching for response validation, making them resilient to minor text changes in bot messages.

### Test Conventions

This package follows the repository-wide testing guidelines from `CLAUDE.md`:

- Tests focus on **observable behavior**, not implementation details
- External systems (Telethon/Telegram) are mocked in unit tests
- No logging assertion tests or trivial dataclass storage tests
- Exception tests verify messages and inheritance for catch-all handling
