"""Formatting service for Telegram bot messages."""

from typing import Any


class JobFormatter:
    """Service for formatting job information into Telegram messages."""

    @staticmethod
    def format_job_message(result: dict[str, Any], job_number: int, total_jobs: int) -> str:
        """Format a job result into a Telegram message.

        Args:
            result: Job result dictionary containing job data and extracted skills
            job_number: Current job number in the sequence
            total_jobs: Total number of jobs being sent

        Returns:
            Formatted message string ready to be sent via Telegram
        """
        job = result["job"]
        skills = result.get("extracted_skills", [])

        # Build message
        message = f"📋 Job {job_number}/{total_jobs}\n\n"
        message += f"🏢 {job.get('title', 'N/A')}\n"
        message += f"🏭 Company: {job.get('company', {}).get('name', 'N/A')}\n"

        # Add salary if available
        if job.get("salary"):
            salary = job["salary"]
            message += f"💰 Salary: {salary.get('currency', '')} {salary.get('min_value', 'N/A')}"
            if salary.get("max_value"):
                message += f" - {salary.get('max_value')}"
            message += "\n"

        # Add location if available
        if job.get("location"):
            location = job["location"]
            message += f"📍 Location: {location.get('region', 'N/A')}"
            if location.get("is_remote"):
                message += " (Remote)"
            message += "\n"

        # Add employment type if available
        if job.get("employment_type"):
            message += f"⏰ Type: {job['employment_type']}\n"

        # Add skills if available
        if skills:
            message += "\n🔧 Must-have skills:\n"
            for skill in skills[:10]:  # Limit to 10 skills to avoid long messages
                message += f"  • {skill}\n"
            if len(skills) > 10:
                message += f"  ... and {len(skills) - 10} more\n"

        # Add URL
        message += f"\n🔗 URL: {job.get('url', 'N/A')}"

        return message

    @staticmethod
    def format_search_summary(
        total_scraped: int,
        passed_filters: int,
        processed: int,
        relevant: int,
    ) -> str:
        """Format search results summary.

        Args:
            total_scraped: Total number of jobs scraped
            passed_filters: Number of jobs that passed filters
            processed: Number of jobs processed
            relevant: Number of relevant jobs found

        Returns:
            Formatted summary message
        """
        return (
            f"✅ Search completed!\n\n"
            f"📊 Results:\n"
            f"• Total scraped: {total_scraped}\n"
            f"• Passed filters: {passed_filters}\n"
            f"• Processed: {processed}\n"
            f"• Relevant jobs: {relevant}\n\n"
            f"Sending relevant jobs..."
        )

    @staticmethod
    def format_search_parameters(salary: int, employment: str, days: int | None) -> str:
        """Format search parameters message.

        Args:
            salary: Minimum salary requirement
            employment: Employment type (e.g., 'remote')
            days: Number of days to look back (None for all jobs)

        Returns:
            Formatted parameters message
        """
        date_info = f"• Last {days} days\n" if days else "• All available jobs\n"
        return (
            f"🔍 Starting job search...\n\n"
            f"Parameters:\n"
            f"• Salary: {salary}\n"
            f"• Employment: {employment}\n"
            f"{date_info}\n"
            f"This may take a few minutes. I'll send you updates as I progress."
        )
