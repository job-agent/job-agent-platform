"""Telegram bot implementation for job agent platform.

This module provides the main bot functionality for interacting with users
via Telegram.
"""

import os
from typing import Optional

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from telegram_bot.handlers import (
    start_handler,
    help_handler,
    search_jobs_handler,
    status_handler,
    cancel_handler,
    upload_cv_handler,
    cv_handler,
)
from telegram_bot.di import build_dependencies
from telegram_bot.access_control import (
    AccessControlConfig,
    parse_allowed_user_ids,
    require_access,
)


class JobAgentBot:
    """Telegram bot for job agent platform.

    This bot allows users to interact with the job agent platform via Telegram,
    triggering job searches and receiving results in their chat.
    """

    def __init__(self, token: str, allowed_user_ids: Optional[str] = None):
        """Initialize the bot.

        Args:
            token: Telegram bot token from BotFather
            allowed_user_ids: Comma-separated list of allowed Telegram user IDs.
                            If None or empty, all users are allowed.
        """
        self.token = token
        self.application: Optional[Application] = None
        self.dependencies = build_dependencies()
        self.access_control_config = AccessControlConfig(
            allowed_ids=parse_allowed_user_ids(allowed_user_ids)
        )

    def setup_handlers(self) -> None:
        """Set up command handlers for the bot.

        All handlers are wrapped with access control to restrict bot usage
        to allowed user IDs when configured.
        """
        if not self.application:
            raise RuntimeError("Application not initialized")

        # Wrap all handlers with access control
        self.application.add_handler(CommandHandler("start", require_access(start_handler)))
        self.application.add_handler(CommandHandler("help", require_access(help_handler)))
        self.application.add_handler(CommandHandler("search", require_access(search_jobs_handler)))
        self.application.add_handler(CommandHandler("status", require_access(status_handler)))
        self.application.add_handler(CommandHandler("cancel", require_access(cancel_handler)))
        self.application.add_handler(CommandHandler("cv", require_access(cv_handler)))

        self.application.add_handler(
            MessageHandler(filters.Document.PDF, require_access(upload_cv_handler))
        )

    async def post_init(self, application: Application) -> None:
        """Called after bot initialization."""
        bot = application.bot
        await bot.set_my_commands(
            [
                ("start", "Start the bot and see welcome message"),
                ("help", "Show help message with available commands"),
                ("search", "Search for jobs (e.g., /search min_salary=4000)"),
                ("status", "Check current search status"),
                ("cancel", "Cancel current job search"),
                ("cv", "View your current CV content"),
            ]
        )

    def build_application(self) -> Application:
        """Build and configure the telegram application.

        Returns:
            Configured Application instance
        """
        self.application = Application.builder().token(self.token).post_init(self.post_init).build()

        self.application.bot_data["dependencies"] = self.dependencies
        self.application.bot_data["access_control"] = self.access_control_config
        self.setup_handlers()
        return self.application

    def run(self) -> None:
        """Run the bot (blocking call)."""
        if not self.application:
            self.build_application()

        print("=" * 60)
        print("Job Agent Telegram Bot")
        print("=" * 60)
        print("Starting bot...")
        print("Bot is running. Press Ctrl+C to stop.")
        print("=" * 60)

        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def create_bot() -> JobAgentBot:
    """Factory function to create a bot instance from environment variables.

    Returns:
        Configured JobAgentBot instance

    Raises:
        ValueError: If TELEGRAM_BOT_TOKEN is not set
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN environment variable is required. "
            "Get a token from @BotFather on Telegram."
        )

    allowed_user_ids = os.getenv("TELEGRAM_ALLOWED_USER_IDS")

    return JobAgentBot(token, allowed_user_ids=allowed_user_ids)
