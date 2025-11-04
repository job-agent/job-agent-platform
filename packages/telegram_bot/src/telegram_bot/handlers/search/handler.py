"""Search command handler for Telegram bot."""

import asyncio
from datetime import datetime, timedelta, timezone

from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.di import get_dependencies

from . import formatter
from ..state import active_searches


async def search_jobs_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /search command.

    Args:
        update: Telegram update object
        context: Callback context

    Examples:
        /search
        /search salary=5000
        /search salary=6000 employment=remote
        /search salary=5000 days=7  # Get jobs from last 7 days
    """
    user_id = update.effective_user.id
    dependencies = get_dependencies(context)
    orchestrator = dependencies.orchestrator_factory()

    if active_searches.get(user_id, False):
        await update.message.reply_text(
            "⚠️ You already have a search running. Please wait for it to complete "
            "or use /cancel to stop it."
        )
        return

    args = context.args or []
    params = {"salary": 4000, "employment": "remote", "days": 1, "timeout": 30}

    for arg in args:
        if "=" in arg:
            key, value = arg.split("=", 1)
            if key in params:
                if key in ("salary", "days", "timeout"):
                    try:
                        params[key] = int(value)
                    except ValueError:
                        await update.message.reply_text(
                            f"❌ Invalid value for {key}: {value}. Must be a number."
                        )
                        return
                else:
                    params[key] = value

    posted_after = None
    if params["days"] is not None:
        posted_after = datetime.now(timezone.utc) - timedelta(days=params["days"])

    if not orchestrator.has_cv(user_id):
        await update.message.reply_text(
            "❌ No CV found!\n\n"
            "Please upload your CV first by sending it as a PDF document to this bot.\n"
            "Once uploaded, you can use /search to find relevant jobs."
        )
        return

    await update.message.reply_text(
        formatter.format_search_parameters(params["salary"], params["employment"], params["days"])
    )

    active_searches[user_id] = True

    try:

        async def telegram_logger(message: str) -> None:
            """Send log messages to the user."""
            await update.message.reply_text(f"ℹ️ {message}")

        def sync_logger(message: str) -> None:
            """Log workflow updates to stdout for orchestrator callbacks."""
            print(f"[Telegram Bot] {message}")

        orchestrator = dependencies.orchestrator_factory(logger=sync_logger)

        loop = asyncio.get_event_loop()

        await update.message.reply_text(
            "📊 Step 1/4: Scraping jobs (will paginate through all pages)..."
        )
        jobs = await loop.run_in_executor(
            None,
            orchestrator.scrape_jobs,
            params["salary"],
            params["employment"],
            posted_after,
            params["timeout"],
        )

        await update.message.reply_text(
            f"✅ Found {len(jobs)} jobs\n\n📊 Step 2/4: Filtering jobs..."
        )
        filtered_jobs = await loop.run_in_executor(None, orchestrator.filter_jobs_list, jobs)

        await update.message.reply_text(
            f"✅ {len(filtered_jobs)}/{len(jobs)} jobs passed filters\n\n"
            f"📊 Step 3/4: Loading your CV..."
        )
        cleaned_cv = await loop.run_in_executor(None, orchestrator.load_cv, user_id)

        await update.message.reply_text(
            f"✅ CV ready\n\n📊 Step 4/4: Processing {len(filtered_jobs)} jobs...\n"
            f"This may take a while..."
        )

        relevant_jobs = []

        for idx, total, result in await loop.run_in_executor(
            None, lambda: list(orchestrator.process_jobs_iterator(filtered_jobs, cleaned_cv))
        ):
            if not active_searches.get(user_id, False):
                await update.message.reply_text("🛑 Search cancelled by user.")
                return

            if result.get("is_relevant"):
                relevant_jobs.append(result)

            if idx % 3 == 0 or idx == total:
                await update.message.reply_text(
                    f"⏳ Processed {idx}/{total} jobs... ({len(relevant_jobs)} relevant)"
                )

        await update.message.reply_text(
            formatter.format_search_summary(
                total_scraped=len(jobs),
                passed_filters=len(filtered_jobs),
                processed=len(filtered_jobs),
                relevant=len(relevant_jobs),
            )
        )

        for idx, result in enumerate(relevant_jobs, 1):
            message = formatter.format_job_message(result, idx, len(relevant_jobs))
            await update.message.reply_text(message)

        if not relevant_jobs:
            await update.message.reply_text(
                "😔 No relevant jobs found matching your CV.\n"
                "Try adjusting your search parameters or check back later."
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
        active_searches[user_id] = False
