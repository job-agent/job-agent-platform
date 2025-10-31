"""Example script demonstrating the multiagent system.

This script shows how to use the multiagent system with sample job data.
"""

from multiagent import run_multiagent_system


def main():
    """Run the multiagent system with sample jobs."""
    # Sample jobs data
    sample_jobs = [
        {
            "title": "Senior Python Developer",
            "salary": 5000,
            "employment": "remote",
            "company": "TechCorp",
            "location": "Remote",
        },
        {
            "title": "Backend Engineer",
            "salary": 6000,
            "employment": "remote",
            "company": "StartupXYZ",
            "location": "Remote",
        },
        {
            "title": "Full Stack Developer",
            "salary": 5500,
            "employment": "remote",
            "company": "DevShop",
            "location": "Remote",
        },
    ]

    print("Starting multiagent system...\n")
    run_multiagent_system(sample_jobs)


if __name__ == "__main__":
    main()
