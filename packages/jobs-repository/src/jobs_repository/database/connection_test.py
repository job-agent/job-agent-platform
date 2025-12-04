"""Tests for database connection management."""

from unittest.mock import patch, MagicMock

import pytest
from sqlalchemy import Engine

from jobs_repository.database.connection import get_engine, reset_engine
from jobs_repository.database.config import DatabaseConfig
from job_agent_platform_contracts.job_repository.exceptions import DatabaseConnectionError


class TestGetEngine:
    """Test suite for get_engine function."""

    def setup_method(self):
        """Reset engine before each test."""
        reset_engine()

    def teardown_method(self):
        """Clean up after each test."""
        reset_engine()

    def test_creates_engine_on_first_call(self):
        """Test that get_engine creates engine on first call."""
        with patch("jobs_repository.database.connection.create_engine") as mock_create:
            mock_engine = MagicMock(spec=Engine)
            mock_connection = MagicMock()
            mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_connection)
            mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
            mock_create.return_value = mock_engine

            engine = get_engine()

            mock_create.assert_called_once()
            assert engine is mock_engine

    def test_reuses_existing_engine(self):
        """Test that get_engine reuses existing engine on subsequent calls."""
        with patch("jobs_repository.database.connection.create_engine") as mock_create:
            mock_engine = MagicMock(spec=Engine)
            mock_connection = MagicMock()
            mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_connection)
            mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
            mock_create.return_value = mock_engine

            engine1 = get_engine()
            engine2 = get_engine()

            mock_create.assert_called_once()
            assert engine1 is engine2

    def test_uses_config_url(self):
        """Test that get_engine uses URL from DatabaseConfig."""
        with patch("jobs_repository.database.connection.create_engine") as mock_create:
            with patch("jobs_repository.database.connection.get_database_config") as mock_config:
                mock_engine = MagicMock(spec=Engine)
                mock_connection = MagicMock()
                mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_connection)
                mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
                mock_create.return_value = mock_engine

                config = DatabaseConfig(url="postgresql://test:5432/testdb")
                mock_config.return_value = config

                get_engine()

                mock_create.assert_called_once_with(
                    "postgresql://test:5432/testdb",
                    pool_pre_ping=True,
                    pool_size=10,
                    max_overflow=20,
                    echo=False,
                )

    def test_uses_config_pool_settings(self):
        """Test that get_engine uses pool settings from DatabaseConfig."""
        with patch("jobs_repository.database.connection.create_engine") as mock_create:
            with patch("jobs_repository.database.connection.get_database_config") as mock_config:
                mock_engine = MagicMock(spec=Engine)
                mock_connection = MagicMock()
                mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_connection)
                mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
                mock_create.return_value = mock_engine

                config = DatabaseConfig(
                    url="postgresql://localhost:5432/jobs",
                    pool_size=15,
                    max_overflow=25,
                    echo=True,
                )
                mock_config.return_value = config

                get_engine()

                mock_create.assert_called_once_with(
                    "postgresql://localhost:5432/jobs",
                    pool_pre_ping=True,
                    pool_size=15,
                    max_overflow=25,
                    echo=True,
                )

    def test_verifies_connection(self):
        """Test that get_engine verifies connection with SELECT 1."""
        with patch("jobs_repository.database.connection.create_engine") as mock_create:
            mock_engine = MagicMock(spec=Engine)
            mock_connection = MagicMock()
            mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_connection)
            mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
            mock_create.return_value = mock_engine

            get_engine()

            mock_connection.execute.assert_called_once()

    def test_raises_database_connection_error_on_failure(self):
        """Test that get_engine raises DatabaseConnectionError on connection failure."""
        with patch("jobs_repository.database.connection.create_engine") as mock_create:
            mock_create.side_effect = Exception("Connection failed")

            with pytest.raises(DatabaseConnectionError) as exc_info:
                get_engine()

            assert "Failed to connect to database" in str(exc_info.value)

    def test_raises_database_connection_error_on_verification_failure(self):
        """Test that get_engine raises error when connection verification fails."""
        with patch("jobs_repository.database.connection.create_engine") as mock_create:
            mock_engine = MagicMock(spec=Engine)
            mock_connection = MagicMock()
            mock_connection.execute.side_effect = Exception("Verification failed")
            mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_connection)
            mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
            mock_create.return_value = mock_engine

            with pytest.raises(DatabaseConnectionError) as exc_info:
                get_engine()

            assert "Failed to connect to database" in str(exc_info.value)


class TestResetEngine:
    """Test suite for reset_engine function."""

    def test_disposes_existing_engine(self):
        """Test that reset_engine disposes existing engine."""
        with patch("jobs_repository.database.connection.create_engine") as mock_create:
            mock_engine = MagicMock(spec=Engine)
            mock_connection = MagicMock()
            mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_connection)
            mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
            mock_create.return_value = mock_engine

            get_engine()
            reset_engine()

            mock_engine.dispose.assert_called_once()

    def test_resets_engine_to_none(self):
        """Test that reset_engine sets engine to None."""
        with patch("jobs_repository.database.connection.create_engine") as mock_create:
            mock_engine = MagicMock(spec=Engine)
            mock_connection = MagicMock()
            mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_connection)
            mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
            mock_create.return_value = mock_engine

            get_engine()
            reset_engine()
            get_engine()

            assert mock_create.call_count == 2

    def test_does_nothing_when_no_engine_exists(self):
        """Test that reset_engine handles case when no engine exists."""
        reset_engine()

    def test_allows_new_engine_creation_after_reset(self):
        """Test that new engine can be created after reset."""
        with patch("jobs_repository.database.connection.create_engine") as mock_create:
            mock_engine1 = MagicMock(spec=Engine)
            mock_engine2 = MagicMock(spec=Engine)
            mock_connection = MagicMock()

            mock_engine1.connect.return_value.__enter__ = MagicMock(return_value=mock_connection)
            mock_engine1.connect.return_value.__exit__ = MagicMock(return_value=False)
            mock_engine2.connect.return_value.__enter__ = MagicMock(return_value=mock_connection)
            mock_engine2.connect.return_value.__exit__ = MagicMock(return_value=False)

            mock_create.side_effect = [mock_engine1, mock_engine2]

            engine1 = get_engine()
            reset_engine()
            engine2 = get_engine()

            assert engine1 is mock_engine1
            assert engine2 is mock_engine2
            assert engine1 is not engine2
