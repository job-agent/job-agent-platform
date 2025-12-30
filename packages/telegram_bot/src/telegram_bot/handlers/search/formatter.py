"""Formatter for search handler messages."""

from typing import Optional

from typing_extensions import TypedDict

from job_scrapper_contracts import JobDict


def _format_2d_skills(skills: list[list[str]], max_skills: int = 10) -> str:
    """Format 2D skill structure for display.

    Skills within inner lists (OR groups) are joined with " or ".
    Groups are joined with ", ".
    Total skill count is limited to max_skills, with remainder shown.

    Args:
        skills: 2D list where outer list = AND groups, inner lists = OR alternatives
        max_skills: Maximum number of individual skills to display

    Returns:
        Formatted string like "JavaScript or Python, React, Docker or Kubernetes"
    """
    if not skills:
        return ""

    # Count total individual skills and format groups
    total_count = 0
    formatted_groups = []

    for group in skills:
        if not group:
            continue

        # Count skills in this group
        group_size = len(group)
        remaining_budget = max_skills - total_count

        if remaining_budget <= 0:
            break

        if group_size <= remaining_budget:
            # Include entire group
            formatted_groups.append(" or ".join(group))
            total_count += group_size
        else:
            # Partial group - take only what fits
            formatted_groups.append(" or ".join(group[:remaining_budget]))
            total_count += remaining_budget
            break

    result = ", ".join(formatted_groups)

    # Calculate total skills across all groups
    total_all = sum(len(group) for group in skills)
    if total_all > max_skills:
        result += f" ... and {total_all - total_count} more"

    return result


class JobResultDict(TypedDict, total=False):
    """Result dictionary containing job data and extracted skills.

    The skill fields use a 2D list format where:
    - The outer list represents AND relationships (all groups are required/preferred)
    - Inner lists represent OR relationships (alternatives within a group)

    Example: [["JavaScript", "Python"], ["React"]] means
    "(JavaScript OR Python) AND React"
    """

    job: JobDict
    extracted_must_have_skills: list[list[str]]
    extracted_nice_to_have_skills: list[list[str]]


def format_job_message(result: JobResultDict, job_number: int, total_jobs: int) -> str:
    """Format a job result into a Telegram message.

    Args:
        result: Job result dictionary containing job data and extracted skills
        job_number: Current job number in the sequence
        total_jobs: Total number of jobs being sent

    Returns:
        Formatted message string ready to be sent via Telegram
    """
    job = result["job"]
    must_have_skills = result.get("extracted_must_have_skills", [])
    nice_to_have_skills = result.get("extracted_nice_to_have_skills", [])

    message = f"📋 Job {job_number}/{total_jobs}\n\n"
    message += f"🏢 {job.get('title', 'N/A')}\n"
    message += f"🏭 Company: {job.get('company', {}).get('name', 'N/A')}\n"

    if job.get("salary"):
        salary = job["salary"]
        message += f"💰 Salary: {salary.get('currency', '')} {salary.get('min_value', 'N/A')}"
        if salary.get("max_value"):
            message += f" - {salary.get('max_value')}"
        message += "\n"

    if job.get("location"):
        location = job["location"]
        message += f"📍 Location: {location.get('region', 'N/A')}"
        if location.get("is_remote"):
            message += " (Remote)"
        message += "\n"

    if job.get("employment_type"):
        message += f"⏰ Type: {job['employment_type']}\n"

    if must_have_skills:
        skills_text = _format_2d_skills(must_have_skills)
        message += f"\n🔧 Must-have skills: {skills_text}"
        message += "\n"

    if nice_to_have_skills:
        skills_text = _format_2d_skills(nice_to_have_skills)
        message += f"\n✨ Nice-to-have skills: {skills_text}"
        message += "\n"

    message += f"\n🔗 URL: {job.get('url', 'N/A')}"

    return message


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


def format_search_parameters(
    min_salary: int,
    employment_location: str,
    days: Optional[int] = None,
) -> str:
    """Format search parameters message.

    Args:
        min_salary: Minimum salary requirement
        employment_location: Employment type (e.g., 'remote')
        days: Number of days to look back (None for auto-calculated default)

    Returns:
        Formatted parameters message
    """
    if days is not None:
        date_info = f"• Last {days} days\n"
    else:
        date_info = "• Using default date range\n"

    return (
        f"🔍 Starting job search...\n\n"
        f"Parameters:\n"
        f"• Min salary: {min_salary}\n"
        f"• Employment: {employment_location}\n"
        f"{date_info}\n"
        f"This may take a few minutes. I'll send you updates as I progress."
    )
