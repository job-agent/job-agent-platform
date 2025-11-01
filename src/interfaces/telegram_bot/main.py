"""Entry point for running the Telegram bot.

Run this module to start the Telegram bot interface:
    python src/interfaces/telegram_bot/main.py

Or as a module:
    python -m src.interfaces.telegram_bot.main
"""

from dotenv import load_dotenv

from interfaces.telegram_bot.bot import create_bot


def main() -> None:
    """Main entry point for the Telegram bot."""
    # Load environment variables
    load_dotenv()

    # Create and run the bot
    bot = create_bot()
    bot.run()


if __name__ == "__main__":
    main()
