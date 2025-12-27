"""Pytest configuration for db-core tests.

This conftest.py sets up the test environment with a default DATABASE_URL.
Tests that need to test missing DATABASE_URL behavior should use
patch.dict(os.environ, ...) to override this default.
"""

import os

import pytest


@pytest.fixture(autouse=True)
def set_database_url(monkeypatch):
    """Set default DATABASE_URL for all tests.

    Individual tests can override this by using:
    - patch.dict(os.environ, {"DATABASE_URL": "..."})
    - patch.dict(os.environ, {}, clear=True) to remove it
    """
    if "DATABASE_URL" not in os.environ:
        monkeypatch.setenv("DATABASE_URL", "postgresql://test:5432/testdb")
