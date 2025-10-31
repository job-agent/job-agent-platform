"""Application connector - wires scrapper service to multiagent system.

This module connects the scrapper service output with the multiagent system input,
serving as the main application entry point.
"""

from dotenv import load_dotenv

from scrapper_service import ScrapperManager
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

    # Step 2: Process jobs with multiagent system
    print("Step 2: Processing jobs with multiagent system...")
    run_multiagent_system(jobs)

    print("\n" + "=" * 60)
    print("Application completed successfully")
    print("=" * 60)

run_application()