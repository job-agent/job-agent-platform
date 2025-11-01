"""Telegram bot implementation for job agent platform.

This module provides the main bot functionality for interacting with users
via Telegram.
"""

import os
from typing import Optional

from telegram import Update
from telegram.ext import Application, CommandHandler

from job_agent_backend.core.orchestrator import JobAgentOrchestrator
from telegram_bot.handlers import (
    start_handler,
    help_handler,
    search_jobs_handler,
    status_handler,
    cancel_handler,
)


class JobAgentBot:
    """Telegram bot for job agent platform.

    This bot allows users to interact with the job agent platform via Telegram,
    triggering job searches and receiving results in their chat.
    """

    def __init__(self, token: str):
        """Initialize the bot.

        Args:
            token: Telegram bot token from BotFather
        """
        self.token = token
        self.application: Optional[Application] = None
        self.orchestrator = JobAgentOrchestrator()

    def setup_handlers(self) -> None:
        """Set up command handlers for the bot."""
        if not self.application:
            raise RuntimeError("Application not initialized")

        # Register command handlers
        self.application.add_handler(CommandHandler("start", start_handler))
        self.application.add_handler(CommandHandler("help", help_handler))
        self.application.add_handler(CommandHandler("search", search_jobs_handler))
        self.application.add_handler(CommandHandler("status", status_handler))
        self.application.add_handler(CommandHandler("cancel", cancel_handler))

    async def post_init(self, application: Application) -> None:
        """Called after bot initialization."""
        bot = application.bot
        await bot.set_my_commands(
            [
                ("start", "Start the bot and see welcome message"),
                ("help", "Show help message with available commands"),
                ("search", "Search for jobs (e.g., /search salary=5000)"),
                ("status", "Check current search status"),
                ("cancel", "Cancel current job search"),
            ]
        )

    def build_application(self) -> Application:
        """Build and configure the telegram application.

        Returns:
            Configured Application instance
        """
        self.application = Application.builder().token(self.token).post_init(self.post_init).build()

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

        # Run the bot until stopped
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

    return JobAgentBot(token)
