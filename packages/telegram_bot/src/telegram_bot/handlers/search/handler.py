"""Search command handler for Telegram bot."""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, Protocol

from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.di import get_dependencies

from . import formatter
from ..state import active_searches

# Maximum days for auto-calculated date range
MAX_AUTO_DAYS = 5

# Default search parameters
DEFAULT_MIN_SALARY = 4000
DEFAULT_EMPLOYMENT_LOCATION = "remote"
DEFAULT_TIMEOUT = 30


class JobRepositoryProtocol(Protocol):
    """Protocol for job repository used in date calculation."""

    def get_latest_updated_at(self) -> Optional[datetime]: ...


@dataclass
class DateCalculationResult:
    """Result of date range calculation for job search."""

    posted_after: Optional[datetime]
    is_auto_calculated: bool
    is_first_search: bool


def _calculate_posted_after(
    explicit_days: Optional[int],
    job_repository: Optional[JobRepositoryProtocol],
) -> DateCalculationResult:
    """Calculate the posted_after date for job search.

    Args:
        explicit_days: Number of days explicitly provided by user, or None
        job_repository: Repository to query for latest job timestamp

    Returns:
        DateCalculationResult with posted_after datetime and metadata flags
    """
    if explicit_days is not None:
        # Explicit days provided - use it directly
        posted_after = datetime.now(timezone.utc) - timedelta(days=explicit_days)
        return DateCalculationResult(
            posted_after=posted_after,
            is_auto_calculated=False,
            is_first_search=False,
        )

    # Auto-calculate from latest job timestamp
    if job_repository is None:
        # Fallback if no repository available
        posted_after = datetime.now(timezone.utc) - timedelta(days=MAX_AUTO_DAYS)
        return DateCalculationResult(
            posted_after=posted_after,
            is_auto_calculated=True,
            is_first_search=True,
        )

    latest_updated_at = job_repository.get_latest_updated_at()

    if latest_updated_at is None:
        # No jobs exist - default to MAX_AUTO_DAYS
        posted_after = datetime.now(timezone.utc) - timedelta(days=MAX_AUTO_DAYS)
        return DateCalculationResult(
            posted_after=posted_after,
            is_auto_calculated=True,
            is_first_search=True,
        )

    # Ensure latest_updated_at is timezone-aware for comparison
    if latest_updated_at.tzinfo is None:
        latest_updated_at = latest_updated_at.replace(tzinfo=timezone.utc)

    # Calculate how many days ago the latest job was updated
    now = datetime.now(timezone.utc)
    days_since_last = (now - latest_updated_at).total_seconds() / (24 * 60 * 60)

    if days_since_last > MAX_AUTO_DAYS:
        # Cap at MAX_AUTO_DAYS
        posted_after = now - timedelta(days=MAX_AUTO_DAYS)
        return DateCalculationResult(
            posted_after=posted_after,
            is_auto_calculated=True,
            is_first_search=True,  # Treat as "catching up"
        )

    # Use the latest job's timestamp
    return DateCalculationResult(
        posted_after=latest_updated_at,
        is_auto_calculated=True,
        is_first_search=False,
    )


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
    params = {
        "min_salary": DEFAULT_MIN_SALARY,
        "employment_location": DEFAULT_EMPLOYMENT_LOCATION,
        "days": None,
        "timeout": DEFAULT_TIMEOUT,
    }
    explicit_days_provided = False

    for arg in args:
        if "=" in arg:
            key, value = arg.split("=", 1)
            if key == "salary":
                await update.message.reply_text(
                    "❌ The parameter 'salary' is no longer supported. Please use 'min_salary'."
                )
                return
            if key in params:
                if key in ("min_salary", "days", "timeout"):
                    try:
                        params[key] = int(value)
                        if key == "days":
                            explicit_days_provided = True
                    except ValueError:
                        await update.message.reply_text(
                            f"❌ Invalid value for {key}: {value}. Must be a number."
                        )
                        return
                else:
                    params[key] = value

    # Calculate posted_after date
    explicit_days = params["days"] if explicit_days_provided else None
    job_repository = None if explicit_days_provided else dependencies.job_repository_factory()

    date_result = _calculate_posted_after(explicit_days, job_repository)
    posted_after = date_result.posted_after
    is_auto_calculated = date_result.is_auto_calculated
    is_first_search = date_result.is_first_search

    if not orchestrator.has_cv(user_id):
        await update.message.reply_text(
            "❌ No CV found!\n\n"
            "Please upload your CV first by sending it as a PDF document to this bot.\n"
            "Once uploaded, you can use /search to find relevant jobs."
        )
        return

    await update.message.reply_text(
        formatter.format_search_parameters(
            params["min_salary"],
            params["employment_location"],
            params["days"],
            posted_after=posted_after,
            is_auto_calculated=is_auto_calculated,
            is_first_search=is_first_search,
        )
    )

    active_searches[user_id] = True

    try:

        def sync_logger(message: str) -> None:
            """Log workflow updates to stdout for orchestrator callbacks."""
            print(f"[Telegram Bot] {message}")

        orchestrator = dependencies.orchestrator_factory(logger=sync_logger)

        loop = asyncio.get_event_loop()

        await update.message.reply_text(
            "📊 Starting job search...\nJobs will be displayed as they're found and processed."
        )

        cleaned_cv = await loop.run_in_executor(None, orchestrator.load_cv, user_id)
        await update.message.reply_text("✅ CV loaded")

        total_scraped = 0
        total_filtered = 0
        total_processed = 0
        relevant_count = 0
        sent_job_count = 0

        def create_streaming_generator():
            return orchestrator.scrape_jobs_streaming(
                params["min_salary"],
                params["employment_location"],
                posted_after,
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
                await update.message.reply_text("🛑 Search cancelled by user.")
                return

            total_scraped = total_jobs_so_far
            await update.message.reply_text(
                f"📄 Scraped {len(batch_jobs)} jobs (total: {total_scraped})"
            )

            filtered_batch = await loop.run_in_executor(
                None, orchestrator.filter_jobs_list, batch_jobs
            )
            total_filtered += len(filtered_batch)

            if not filtered_batch:
                await update.message.reply_text("⏭️  No jobs passed filters, continuing...")
                continue

            await update.message.reply_text(
                f"🔍 {len(filtered_batch)} jobs passed filters, processing..."
            )

            batch_relevant = []
            for idx, total_batch, result in await loop.run_in_executor(
                None,
                lambda fb=filtered_batch: list(orchestrator.process_jobs_iterator(fb, cleaned_cv)),
            ):
                if not active_searches.get(user_id, False):
                    await update.message.reply_text("🛑 Search cancelled by user.")
                    return

                total_processed += 1

                if result.get("is_relevant"):
                    batch_relevant.append(result)
                    relevant_count += 1

            if batch_relevant:
                await update.message.reply_text(f"✨ Found {len(batch_relevant)} relevant job(s)!")

                for result in batch_relevant:
                    sent_job_count += 1
                    message = formatter.format_job_message(result, sent_job_count, relevant_count)
                    await update.message.reply_text(message)
            else:
                await update.message.reply_text(
                    f"⏭️  Processed {len(filtered_batch)} jobs, none relevant"
                )

        await update.message.reply_text(
            formatter.format_search_summary(
                total_scraped=total_scraped,
                passed_filters=total_filtered,
                processed=total_processed,
                relevant=relevant_count,
            )
        )

        if relevant_count == 0:
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
