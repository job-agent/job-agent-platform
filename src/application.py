"""Application connector - wires scrapper service to multiagent system.

This module connects the scrapper service output with the multiagent system input,
serving as the main application entry point.
"""

import os

from dotenv import load_dotenv
from scrapper_service import ScrapperManager

from filter_service import FilterConfig, filter_jobs
from multiagent import run_multiagent_system

# Load environment variables from .env file
load_dotenv()


def run_application(
    salary: int = 4000,
    employment: str = "remote",
    page: int = 1,
    timeout: int = 30
) -> None:
    """
    Run the complete application: scrape jobs and process them with agents.

    This is the main entry point that connects the scrapper service with
    the multiagent system. It scrapes jobs using ScrapperManager and passes
    them to the multiagent workflow for processing.

    Args:
        salary: Minimum salary filter (default: 4000)
        employment: Employment type filter (default: "remote")
        page: Page number for pagination (default: 1)
        timeout: Request timeout in seconds (default: 30)

    Example:
        >>> run_application(salary=5000, employment="remote")
    """
    print("=" * 60)
    print("Starting Job Agent Application")
    print("=" * 60)
    print()

    # Step 1: Scrape jobs using scrapper service
    print("Step 1: Scraping jobs...")
    scrapper_manager = ScrapperManager()
    jobs = scrapper_manager.scrape_jobs_as_dicts(
        salary=salary,
        employment=employment,
        page=page,
        timeout=timeout
    )
    print(f"✓ Scraped {len(jobs)} jobs\n")

    # Step 2: Filter unsuitable jobs
    print("Step 2: Filtering jobs...")

    # Build filter config from environment variables
    filter_config: FilterConfig = {}

    if os.getenv("FILTER_MAX_MONTHS_OF_EXPERIENCE"):
        filter_config["max_months_of_experience"] = int(os.getenv("FILTER_MAX_MONTHS_OF_EXPERIENCE"))

    if os.getenv("FILTER_LOCATION_ALLOWS_TO_APPLY"):
        filter_config["location_allows_to_apply"] = os.getenv("FILTER_LOCATION_ALLOWS_TO_APPLY").lower() in ("true", "1", "yes")

    filtered_jobs = filter_jobs(jobs, filter_config)
    print(f"✓ Filtered jobs: {len(filtered_jobs)}/{len(jobs)} jobs passed\n")

    # Step 3: Process jobs with multiagent system
    print("Step 3: Processing jobs with multiagent system...")
    run_multiagent_system(filtered_jobs)

    print("\n" + "=" * 60)
    print("Application completed successfully")
    print("=" * 60)

run_application()