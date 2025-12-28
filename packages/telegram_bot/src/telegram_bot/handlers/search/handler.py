"""Search command handler for Telegram bot."""

import asyncio
import logging
import traceback
from typing import Any

from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.di import get_dependencies

from . import formatter
from .params import parse_search_params
from ..state import active_searches

logger = logging.getLogger(__name__)


async def search_jobs_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /search command.

    Args:
        update: Telegram update object
        context: Callback context

    Examples:
        /search
        /search min_salary=4000
        /search min_salary=6000 employment_location=remote
        /search min_salary=5000 days=7  # Get jobs from last 7 days
    """
    if update.message is None or update.effective_user is None:
        return
    message = update.message
    user_id = update.effective_user.id
    dependencies = get_dependencies(context)
    orchestrator = dependencies.orchestrator_factory()

    if active_searches.get(user_id, False):
        await message.reply_text(
            "You already have a search running. Please wait for it to complete "
            "or use /cancel to stop it."
        )
        return

    args = context.args or []
    params, error = parse_search_params(args)

    if error is not None:
        await message.reply_text(f"Error: {error.message}")
        return

    if not orchestrator.has_cv(user_id):
        await message.reply_text(
            "❌ No CV found!\n\n"
            "Please upload your CV first by sending it as a PDF document to this bot.\n"
            "Once uploaded, you can use /search to find relevant jobs."
        )
        return

    await message.reply_text(
        formatter.format_search_parameters(
            params["min_salary"],
            params["employment_location"],
            params["days"],
        )
    )

    active_searches[user_id] = True

    try:

        def sync_logger(log_message: str) -> None:
            """Log workflow updates to stdout for orchestrator callbacks."""
            print(f"[Telegram Bot] {log_message}")

        orchestrator = dependencies.orchestrator_factory(logger=sync_logger)

        loop = asyncio.get_running_loop()

        await message.reply_text(
            "📊 Starting job search...\nJobs will be displayed as they're found and processed."
        )

        cleaned_cv = await loop.run_in_executor(None, orchestrator.load_cv, user_id)
        await message.reply_text("✅ CV loaded")

        total_scraped = 0
        total_filtered = 0
        total_processed = 0
        relevant_count = 0
        sent_job_count = 0

        def create_streaming_generator():
            return orchestrator.scrape_jobs_streaming(
                params["min_salary"],
                params["employment_location"],
                params["days"],
                params["timeout"],
            )

        streaming_gen = await loop.run_in_executor(None, create_streaming_generator)

        def get_next_batch(gen):
            try:
                return next(gen), False
            except StopIteration:
                return None, True

        while True:
            batch_result, is_done = await loop.run_in_executor(None, get_next_batch, streaming_gen)

            if is_done:
                break

            batch_jobs, total_jobs_so_far = batch_result

            if not active_searches.get(user_id, False):
                await message.reply_text("🛑 Search cancelled by user.")
                return

            total_scraped = total_jobs_so_far
            await message.reply_text(f"📄 Scraped {len(batch_jobs)} jobs (total: {total_scraped})")

            filtered_batch = await loop.run_in_executor(
                None, orchestrator.filter_jobs_list, batch_jobs
            )
            total_filtered += len(filtered_batch)

            if not filtered_batch:
                await message.reply_text("⏭️  No jobs passed filters, continuing...")
                continue

            await message.reply_text(f"🔍 {len(filtered_batch)} jobs passed filters, processing...")

            def process_batch() -> list[tuple[int, int, Any]]:
                return list(orchestrator.process_jobs_iterator(filtered_batch, cleaned_cv))

            batch_relevant = []
            for idx, total_batch, result in await loop.run_in_executor(None, process_batch):
                if not active_searches.get(user_id, False):
                    await message.reply_text("🛑 Search cancelled by user.")
                    return

                total_processed += 1

                if result.get("is_relevant"):
                    batch_relevant.append(result)
                    relevant_count += 1

            if batch_relevant:
                await message.reply_text(f"✨ Found {len(batch_relevant)} relevant job(s)!")

                for result in batch_relevant:
                    sent_job_count += 1
                    job_message = formatter.format_job_message(
                        result, sent_job_count, relevant_count
                    )
                    await message.reply_text(job_message)
            else:
                await message.reply_text(f"⏭️  Processed {len(filtered_batch)} jobs, none relevant")

        await message.reply_text(
            formatter.format_search_summary(
                total_scraped=total_scraped,
                passed_filters=total_filtered,
                processed=total_processed,
                relevant=relevant_count,
            )
        )

        if relevant_count == 0:
            await message.reply_text(
                "😔 No relevant jobs found matching your CV.\n"
                "Try adjusting your search parameters or check back later."
            )

    except Exception as e:
        logger.error("Error during job search: %s", e)
        logger.debug("Search error traceback:\n%s", traceback.format_exc())
        await message.reply_text(
            "❌ An error occurred during the search.\n\n"
            "Please try again or contact support if the issue persists."
        )

    finally:
        active_searches[user_id] = False
