# Telegram Bot

Telegram bot interface for the Job Agent platform, allowing users to interact with the job agent system through Telegram.

## Features

- **Job Search**: Search for jobs directly through Telegram commands
- **Status Monitoring**: Check the status of ongoing job searches
- **Interactive Commands**: User-friendly command interface
- **Async Support**: Built with python-telegram-bot for efficient async operations

## Installation

From the monorepo root:

```bash
# Install backend first (required dependency)
pip install -e packages/job-agent-backend

# Then install telegram bot
pip install -e packages/telegram-bot
```

Or with development dependencies:

```bash
pip install -e "packages/telegram_bot[dev]"
```

## Configuration

Set up your environment variables in `.env`:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
```

Get a bot token from [@BotFather](https://t.me/botfather) on Telegram.

## Usage

Run the bot:

```bash
python -m telegram-bot.main
```

Or from the package directory:

```bash
cd packages/telegram-bot
python src/telegram-bot/main.py
```

## Available Commands

- `/start` - Start the bot and see welcome message
- `/help` - Show help message with available commands
- `/search` - Search for jobs (e.g., /search salary=5000)
- `/status` - Check current search status
- `/cancel` - Cancel current job search

## Structure

```
telegram_bot/
├── src/
│   └── telegram_bot/
│       ├── bot.py       # Main bot implementation
│       ├── handlers.py  # Command handlers
│       └── main.py      # Entry point
├── tests/              # Unit tests
└── pyproject.toml     # Package configuration
```

## Dependencies

- python-telegram-bot >= 21.0
- job-agent-backend (from this monorepo)

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black src/
ruff check src/
```
