"""Tests for database configuration module."""

import os
from contextlib import contextmanager
from unittest.mock import patch

import pytest

from db_core.config import DatabaseConfig, get_database_config


@contextmanager
def _without_database_url():
    """Context manager that removes DATABASE_URL from the environment.

    This encapsulates the pattern of clearing DATABASE_URL for tests
    that verify behavior when the environment variable is not set.
    """
    env = {k: v for k, v in os.environ.items() if k != "DATABASE_URL"}
    with patch.dict(os.environ, env, clear=True):
        yield


class TestDatabaseConfig:
    """Test suite for DatabaseConfig Pydantic model."""

    def test_url_reads_from_database_url_env_var(self):
        """DatabaseConfig should read URL from DATABASE_URL environment variable."""
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://test:5432/mydb"}):
            config = DatabaseConfig()

            assert config.url == "postgresql://test:5432/mydb"

    def test_url_requires_database_url_env_var(self):
        """DatabaseConfig should require DATABASE_URL when not set."""
        with _without_database_url():
            with pytest.raises(ValueError) as exc_info:
                DatabaseConfig()

            assert "DATABASE_URL" in str(exc_info.value)

    def test_url_can_be_explicitly_provided(self):
        """DatabaseConfig accepts explicitly provided URL."""
        config = DatabaseConfig(url="postgresql://explicit:5432/explicit_db")

        assert config.url == "postgresql://explicit:5432/explicit_db"


class TestGetDatabaseConfig:
    """Test suite for get_database_config function."""

    def test_reads_url_from_environment(self):
        """get_database_config should read DATABASE_URL from environment."""
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://env:5432/envdb"}):
            config = get_database_config()

            assert config.url == "postgresql://env:5432/envdb"

    def test_raises_when_database_url_missing(self):
        """get_database_config should raise when DATABASE_URL is not set."""
        with _without_database_url():
            with pytest.raises(ValueError) as exc_info:
                get_database_config()

            assert "DATABASE_URL" in str(exc_info.value)


class TestDatabaseConfigValidation:
    """Test DatabaseConfig field validation."""

    def test_pool_size_must_be_positive(self):
        """pool_size should be a positive integer."""
        with pytest.raises(ValueError):
            DatabaseConfig(url="postgresql://test:5432/db", pool_size=-1)

    def test_pool_size_must_be_integer(self):
        """pool_size should reject non-integer values."""
        with pytest.raises((ValueError, TypeError)):
            DatabaseConfig(url="postgresql://test:5432/db", pool_size="invalid")

    def test_max_overflow_must_be_non_negative(self):
        """max_overflow should be non-negative (0 or positive)."""
        # 0 is valid - means no overflow connections allowed
        config = DatabaseConfig(url="postgresql://test:5432/db", max_overflow=0)
        assert config.max_overflow == 0

        # Negative should fail
        with pytest.raises(ValueError):
            DatabaseConfig(url="postgresql://test:5432/db", max_overflow=-1)

    def test_echo_must_be_boolean(self):
        """echo should be a boolean value."""
        with pytest.raises((ValueError, TypeError)):
            DatabaseConfig(url="postgresql://test:5432/db", echo="yes")
