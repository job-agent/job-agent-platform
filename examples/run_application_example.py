"""Example script demonstrating the full application.

This script shows how to run the complete job agent application,
connecting scrapper service with the multiagent system.
"""

from application import run_application


def main():
    """Run the full job agent application."""
    # Run with default parameters
    run_application(
        salary=4000,
        employment="remote",
        page=1,
        timeout=30
    )


if __name__ == "__main__":
    main()
