"""Entry point for running the Telegram bot.

Run this module to start the Telegram bot interface:
    python -m telegram_bot.main

Or from the package directory:
    python src/telegram_bot/main.py
"""

import argparse
import logging

from dotenv import load_dotenv

from telegram_bot.bot import create_bot


def main() -> None:
    """Main entry point for the Telegram bot."""
    parser = argparse.ArgumentParser(description="Job Agent Telegram Bot")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate startup (imports, dependencies, handlers) and exit without polling",
    )

    args = parser.parse_args()

    load_dotenv()

    # Configure logging to show INFO level messages
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger = logging.getLogger(__name__)

    logger.info("Initializing Telegram bot...")
    bot = create_bot()
    bot.build_application()

    if args.check:
        logger.info("Startup check passed: bot initialized successfully")
        return

    bot.run()


if __name__ == "__main__":
    main()
