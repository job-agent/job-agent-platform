"""Tests for database configuration."""

import os
from unittest.mock import patch


from jobs_repository.database.config import DatabaseConfig, get_database_config


class TestDatabaseConfig:
    """Test suite for DatabaseConfig class."""

    def test_default_values(self):
        """Test DatabaseConfig with default values."""
        with patch.dict(os.environ, {}, clear=True):
            with patch.dict(os.environ, {"DATABASE_URL": "postgresql://localhost:5432/jobs"}):
                config = DatabaseConfig()

                assert config.url == "postgresql://localhost:5432/jobs"
                assert config.pool_size == 10
                assert config.max_overflow == 20
                assert config.echo is False

    def test_custom_url_from_env(self):
        """Test DatabaseConfig reads URL from DATABASE_URL env variable."""
        custom_url = "postgresql://user:pass@host:5432/dbname"
        with patch.dict(os.environ, {"DATABASE_URL": custom_url}):
            config = DatabaseConfig()

            assert config.url == custom_url

    def test_missing_database_url_uses_default(self):
        """Test DatabaseConfig uses default URL when DATABASE_URL not set."""
        with patch.dict(os.environ, {}, clear=True):
            config = DatabaseConfig()

            assert config.url == "postgresql://localhost:5432/jobs"

    def test_custom_pool_size(self):
        """Test DatabaseConfig with custom pool_size."""
        config = DatabaseConfig(pool_size=5)

        assert config.pool_size == 5

    def test_custom_max_overflow(self):
        """Test DatabaseConfig with custom max_overflow."""
        config = DatabaseConfig(max_overflow=10)

        assert config.max_overflow == 10

    def test_custom_echo(self):
        """Test DatabaseConfig with echo enabled."""
        config = DatabaseConfig(echo=True)

        assert config.echo is True

    def test_all_custom_values(self):
        """Test DatabaseConfig with all custom values."""
        config = DatabaseConfig(
            url="postgresql://custom:5432/test",
            pool_size=15,
            max_overflow=30,
            echo=True,
        )

        assert config.url == "postgresql://custom:5432/test"
        assert config.pool_size == 15
        assert config.max_overflow == 30
        assert config.echo is True

    def test_field_types(self):
        """Test that DatabaseConfig fields have correct types."""
        config = DatabaseConfig()

        assert isinstance(config.url, str)
        assert isinstance(config.pool_size, int)
        assert isinstance(config.max_overflow, int)
        assert isinstance(config.echo, bool)


class TestGetDatabaseConfig:
    """Test suite for get_database_config function."""

    def test_returns_database_config_instance(self):
        """Test that get_database_config returns DatabaseConfig instance."""
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://localhost:5432/test"}):
            config = get_database_config()

            assert isinstance(config, DatabaseConfig)

    def test_reads_from_environment(self):
        """Test that get_database_config reads from environment."""
        custom_url = "postgresql://testuser:testpass@testhost:5432/testdb"
        with patch.dict(os.environ, {"DATABASE_URL": custom_url}):
            config = get_database_config()

            assert config.url == custom_url

    def test_multiple_calls_create_new_instances(self):
        """Test that multiple calls to get_database_config create new instances."""
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://localhost:5432/test"}):
            config1 = get_database_config()
            config2 = get_database_config()

            assert isinstance(config1, DatabaseConfig)
            assert isinstance(config2, DatabaseConfig)
            assert config1 is not config2
