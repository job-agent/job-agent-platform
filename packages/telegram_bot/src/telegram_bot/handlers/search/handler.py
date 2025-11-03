"""Search command handler for Telegram bot."""

import asyncio
from datetime import datetime, timedelta, timezone

from telegram import Update
from telegram.ext import ContextTypes

from job_agent_backend.core.orchestrator import JobAgentOrchestrator
from jobs_repository.database.session import get_db_session

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

    # Check if user already has an active search
    if active_searches.get(user_id, False):
        await update.message.reply_text(
            "⚠️ You already have a search running. Please wait for it to complete "
            "or use /cancel to stop it."
        )
        return

    # Parse arguments
    args = context.args or []
    params = {"salary": 4000, "employment": "remote", "days": 1, "timeout": 30}

    # Parse key=value arguments
    for arg in args:
        if "=" in arg:
            key, value = arg.split("=", 1)
            if key in params:
                # Convert to appropriate type
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

    # Calculate posted_after date if days parameter provided
    posted_after = None
    if params["days"] is not None:
        posted_after = datetime.now(timezone.utc) - timedelta(days=params["days"])

    # Check if user has uploaded a CV
    orchestrator = JobAgentOrchestrator()
    if not orchestrator.has_cv(user_id):
        await update.message.reply_text(
            "❌ No CV found!\n\n"
            "Please upload your CV first by sending it as a PDF document to this bot.\n"
            "Once uploaded, you can use /search to find relevant jobs."
        )
        return

    # Send initial confirmation
    await update.message.reply_text(
        formatter.format_search_parameters(params["salary"], params["employment"], params["days"])
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
            f"📊 Step 3/4: Loading and cleaning your CV..."
        )
        cleaned_cv = await loop.run_in_executor(
            None,
            lambda: orchestrator.load_and_clean_cv(user_id=user_id)
        )

        await update.message.reply_text(
            f"✅ CV ready\n\n📊 Step 4/4: Processing {len(filtered_jobs)} jobs...\n"
            f"This may take a while..."
        )

        # Create database session for processing jobs
        # (migrations are run automatically on container startup)
        db_gen = get_db_session()
        db_session = next(db_gen)

        relevant_jobs = []

        try:
            # Process jobs
            for idx, job in enumerate(filtered_jobs, 1):
                # Check if user cancelled
                if not active_searches.get(user_id, False):
                    await update.message.reply_text("🛑 Search cancelled by user.")
                    return

                result = await loop.run_in_executor(
                    None, orchestrator.process_job, job, cleaned_cv, db_session
                )

                # Collect relevant jobs
                if result.get("is_relevant"):
                    relevant_jobs.append(result)

                # Send progress update every 3 jobs
                if idx % 3 == 0 or idx == len(filtered_jobs):
                    await update.message.reply_text(
                        f"⏳ Processed {idx}/{len(filtered_jobs)} jobs... ({len(relevant_jobs)} relevant)"
                    )
        finally:
            # Always close the database session
            db_session.close()

        # Send final results summary
        await update.message.reply_text(
            formatter.format_search_summary(
                total_scraped=len(jobs),
                passed_filters=len(filtered_jobs),
                processed=len(filtered_jobs),
                relevant=len(relevant_jobs),
            )
        )

        # Send each relevant job to the user
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
        # Mark search as inactive
        active_searches[user_id] = False
