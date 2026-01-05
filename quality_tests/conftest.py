"""Pytest configuration and fixtures for quality tests.

Quality tests verify code quality:
- Type checking (mypy)
"""

from pathlib import Path

import pytest


# Ensure project root is in path for imports
PROJECT_ROOT = Path(__file__).parent.parent
PACKAGES_DIR = PROJECT_ROOT / "packages"


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory path."""
    return PROJECT_ROOT


@pytest.fixture
def packages_dir() -> Path:
    """Return the packages directory path."""
    return PACKAGES_DIR


@pytest.fixture
def package_names() -> list[str]:
    """Return list of all package names in job-agent-platform."""
    return [
        "db_core",
        "job_agent_backend",
        "job_agent_platform_contracts",
        "jobs_repository",
        "essay_repository",
        "cvs_repository",
        "telegram_bot",
    ]


@pytest.fixture
def package_source_dirs() -> dict[str, Path]:
    """Return mapping of package names to their source directories."""
    return {
        "db_core": PACKAGES_DIR / "db-core" / "src" / "db_core",
        "job_agent_backend": PACKAGES_DIR / "job-agent-backend" / "src" / "job_agent_backend",
        "job_agent_platform_contracts": (
            PACKAGES_DIR / "job-agent-platform-contracts" / "src" / "job_agent_platform_contracts"
        ),
        "jobs_repository": PACKAGES_DIR / "jobs-repository" / "src" / "jobs_repository",
        "essay_repository": PACKAGES_DIR / "essay-repository" / "src" / "essay_repository",
        "cvs_repository": PACKAGES_DIR / "cvs-repository" / "src" / "cvs_repository",
        "telegram_bot": PACKAGES_DIR / "telegram_bot" / "src" / "telegram_bot",
    }
