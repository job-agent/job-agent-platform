"""Command handlers for Telegram bot.

This module contains all the command handlers that respond to user commands
in the Telegram bot.
"""

import asyncio
from typing import Dict, Any

from telegram import Update
from telegram.ext import ContextTypes

from job_agent_backend.core.orchestrator import JobAgentOrchestrator


# Store active searches per user
active_searches: Dict[int, bool] = {}


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Hello {user.first_name}!\n\n"
        "I'm the Job Agent Bot. I help you find and analyze job opportunities "
        "that match your profile.\n\n"
        "Use /help to see available commands."
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command.

    Args:
        update: Telegram update object
        context: Callback context
    """
    help_text = """
📚 Available Commands:

/start - Start the bot and see welcome message
/help - Show this help message
/search - Search for jobs with optional parameters
/status - Check if a search is currently running
/cancel - Cancel the current job search

🔍 Search Examples:

/search
  → Search with default parameters (salary=4000, remote)

/search salary=5000
  → Search for jobs with minimum salary of 5000

/search salary=6000 employment=remote page=1
  → Custom search with multiple parameters

⚙️ Available Parameters:
- salary: Minimum salary (default: 4000)
- employment: Employment type (default: "remote")
- page: Page number (default: 1)
- timeout: Request timeout in seconds (default: 30)

📝 Note: Job results are processed using your CV and sent back to you automatically.
"""
    await update.message.reply_text(help_text)


async def search_jobs_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /search command.

    Args:
        update: Telegram update object
        context: Callback context

    Examples:
        /search
        /search salary=5000
        /search salary=6000 employment=remote page=1
    """
    user_id = update.effective_user.id

    # Check if user already has an active search
    if active_searches.get(user_id, False):
        await update.message.reply_text(
            "⚠️ You already have a search running. Please wait for it to complete "
            "or use /cancel to stop it."
        )
        return

    # Parse arguments
    args = context.args or []
    params = {
        "salary": 4000,
        "employment": "remote",
        "page": 1,
        "timeout": 30
    }

    # Parse key=value arguments
    for arg in args:
        if "=" in arg:
            key, value = arg.split("=", 1)
            if key in params:
                # Convert to appropriate type
                if key in ("salary", "page", "timeout"):
                    try:
                        params[key] = int(value)
                    except ValueError:
                        await update.message.reply_text(
                            f"❌ Invalid value for {key}: {value}. Must be a number."
                        )
                        return
                else:
                    params[key] = value

    # Send initial confirmation
    await update.message.reply_text(
        f"🔍 Starting job search...\n\n"
        f"Parameters:\n"
        f"• Salary: {params['salary']}\n"
        f"• Employment: {params['employment']}\n"
        f"• Page: {params['page']}\n\n"
        f"This may take a few minutes. I'll send you updates as I progress."
    )

    # Mark search as active
    active_searches[user_id] = True

    try:
        # Create logger that sends messages to telegram
        async def telegram_logger(message: str) -> None:
            """Send log messages to the user."""
            await update.message.reply_text(f"ℹ️ {message}")

        # Create orchestrator with telegram logger
        def sync_logger(message: str) -> None:
            """Wrapper to call async logger from sync code."""
            # We'll collect messages and send them in batches
            print(f"[Telegram Bot] {message}")

        orchestrator = JobAgentOrchestrator(logger=sync_logger)

        # Run the pipeline in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()

        await update.message.reply_text("📊 Step 1/4: Scraping jobs...")
        jobs = await loop.run_in_executor(
            None,
            orchestrator.scrape_jobs,
            params["salary"],
            params["employment"],
            params["page"],
            params["timeout"]
        )

        await update.message.reply_text(
            f"✅ Found {len(jobs)} jobs\n\n📊 Step 2/4: Filtering jobs..."
        )
        filtered_jobs = await loop.run_in_executor(
            None,
            orchestrator.filter_jobs_list,
            jobs
        )

        await update.message.reply_text(
            f"✅ {len(filtered_jobs)}/{len(jobs)} jobs passed filters\n\n"
            f"📊 Step 3/4: Loading and cleaning your CV..."
        )
        cleaned_cv = await loop.run_in_executor(
            None,
            orchestrator.load_and_clean_cv
        )

        await update.message.reply_text(
            f"✅ CV ready\n\n📊 Step 4/4: Processing {len(filtered_jobs)} jobs...\n"
            f"This may take a while..."
        )

        # Process jobs
        for idx, job in enumerate(filtered_jobs, 1):
            # Check if user cancelled
            if not active_searches.get(user_id, False):
                await update.message.reply_text("🛑 Search cancelled by user.")
                return

            await loop.run_in_executor(
                None,
                orchestrator.process_job,
                job,
                cleaned_cv
            )

            # Send progress update every 3 jobs
            if idx % 3 == 0 or idx == len(filtered_jobs):
                await update.message.reply_text(f"⏳ Processed {idx}/{len(filtered_jobs)} jobs...")

        # Send final results
        await update.message.reply_text(
            f"✅ Search completed!\n\n"
            f"📊 Results:\n"
            f"• Total scraped: {len(jobs)}\n"
            f"• Passed filters: {len(filtered_jobs)}\n"
            f"• Processed: {len(filtered_jobs)}\n\n"
            f"Check the logs for detailed analysis of each job."
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Error during search: {str(e)}\n\n"
            f"Please try again or contact support if the issue persists."
        )
        print(f"Error in search: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Mark search as inactive
        active_searches[user_id] = False


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /status command.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user_id = update.effective_user.id
    is_active = active_searches.get(user_id, False)

    if is_active:
        await update.message.reply_text(
            "⏳ You have an active job search running.\n\n"
            "Use /cancel to stop it."
        )
    else:
        await update.message.reply_text(
            "✅ No active searches.\n\n"
            "Use /search to start a new job search."
        )


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /cancel command.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user_id = update.effective_user.id
    is_active = active_searches.get(user_id, False)

    if is_active:
        active_searches[user_id] = False
        await update.message.reply_text(
            "🛑 Cancelling your job search...\n\n"
            "The search will stop after the current job finishes processing."
        )
    else:
        await update.message.reply_text(
            "ℹ️ No active search to cancel.\n\n"
            "Use /search to start a new job search."
        )
