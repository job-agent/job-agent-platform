"""Entry point for running the Telegram bot.

Run this module to start the Telegram bot interface:
    python -m telegram-bot.main

Or from the package directory:
    python src/telegram-bot/main.py
"""

from dotenv import load_dotenv

from telegram_bot.bot import create_bot


def main() -> None:
    """Main entry point for the Telegram bot."""
    load_dotenv()

    bot = create_bot()
    bot.run()


if __name__ == "__main__":
    main()
