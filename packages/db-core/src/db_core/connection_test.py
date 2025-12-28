"""Tests for database connection management."""

from unittest.mock import patch, MagicMock
import threading

import pytest
from sqlalchemy import Engine

from db_core.connection import get_engine, reset_engine
from db_core.config import DatabaseConfig
from db_core.exceptions import DatabaseConnectionError


def _create_mock_engine():
    """Create a properly configured mock engine with connection context manager setup.

    Returns:
        tuple: (mock_engine, mock_connection) - the mock engine and its mock connection.
    """
    mock_engine = MagicMock(spec=Engine)
    mock_connection = MagicMock()
    mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_connection)
    mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
    return mock_engine, mock_connection


@pytest.fixture(autouse=True)
def reset_engine_singleton():
    """Reset engine singleton before and after each test."""
    reset_engine()
    yield
    reset_engine()


class TestGetEngine:
    """Test suite for get_engine function."""

    def test_creates_engine_on_first_call(self):
        """get_engine creates engine on first call."""
        with patch("db_core.connection.create_engine") as mock_create:
            mock_engine, _ = _create_mock_engine()
            mock_create.return_value = mock_engine

            engine = get_engine()

            mock_create.assert_called_once()
            assert engine is mock_engine

    def test_reuses_existing_engine_singleton(self):
        """get_engine reuses existing engine on subsequent calls (singleton pattern)."""
        with patch("db_core.connection.create_engine") as mock_create:
            mock_engine, _ = _create_mock_engine()
            mock_create.return_value = mock_engine

            engine1 = get_engine()
            engine2 = get_engine()

            mock_create.assert_called_once()
            assert engine1 is engine2

    def test_uses_config_url(self):
        """get_engine uses URL from DatabaseConfig."""
        with patch("db_core.connection.create_engine") as mock_create:
            with patch("db_core.connection.get_database_config") as mock_config:
                mock_engine, _ = _create_mock_engine()
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
        """get_engine uses pool settings from DatabaseConfig."""
        with patch("db_core.connection.create_engine") as mock_create:
            with patch("db_core.connection.get_database_config") as mock_config:
                mock_engine, _ = _create_mock_engine()
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

    def test_verifies_connection_with_select_1(self):
        """get_engine verifies connection with SELECT 1."""
        with patch("db_core.connection.create_engine") as mock_create:
            mock_engine, mock_connection = _create_mock_engine()
            mock_create.return_value = mock_engine

            get_engine()

            mock_connection.execute.assert_called_once()

    def test_enables_pool_pre_ping(self):
        """get_engine enables pool_pre_ping for connection validation."""
        with patch("db_core.connection.create_engine") as mock_create:
            with patch("db_core.connection.get_database_config") as mock_config:
                mock_engine, _ = _create_mock_engine()
                mock_create.return_value = mock_engine

                config = DatabaseConfig(url="postgresql://test:5432/db")
                mock_config.return_value = config

                get_engine()

                call_kwargs = mock_create.call_args[1]
                assert call_kwargs["pool_pre_ping"] is True


class TestGetEngineErrorHandling:
    """Test suite for get_engine error handling."""

    def test_raises_database_connection_error_on_creation_failure(self):
        """get_engine raises DatabaseConnectionError on engine creation failure."""
        with patch("db_core.connection.create_engine") as mock_create:
            mock_create.side_effect = Exception("Connection failed")

            with pytest.raises(DatabaseConnectionError) as exc_info:
                get_engine()

            assert "Failed to connect to database" in str(exc_info.value)

    def test_raises_database_connection_error_on_verification_failure(self):
        """get_engine raises DatabaseConnectionError when connection verification fails."""
        with patch("db_core.connection.create_engine") as mock_create:
            mock_engine, mock_connection = _create_mock_engine()
            mock_connection.execute.side_effect = Exception("Verification failed")
            mock_create.return_value = mock_engine

            with pytest.raises(DatabaseConnectionError) as exc_info:
                get_engine()

            assert "Failed to connect to database" in str(exc_info.value)

    def test_preserves_original_exception_as_cause(self):
        """DatabaseConnectionError preserves original exception in chain."""
        with patch("db_core.connection.create_engine") as mock_create:
            original_error = Exception("Original connection error")
            mock_create.side_effect = original_error

            with pytest.raises(DatabaseConnectionError) as exc_info:
                get_engine()

            assert exc_info.value.__cause__ is original_error


class TestGetEngineThreadSafety:
    """Test suite for get_engine thread safety."""

    def test_thread_safe_engine_creation(self):
        """get_engine is thread-safe - multiple threads get same engine."""
        with patch("db_core.connection.create_engine") as mock_create:
            mock_engine, _ = _create_mock_engine()
            mock_create.return_value = mock_engine

            engines = []
            errors = []

            def get_engine_thread():
                try:
                    engine = get_engine()
                    engines.append(engine)
                except Exception as e:
                    errors.append(e)

            threads = [threading.Thread(target=get_engine_thread) for _ in range(10)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            assert len(errors) == 0
            assert len(engines) == 10
            assert all(e is engines[0] for e in engines)
            # Engine should only be created once despite concurrent access
            mock_create.assert_called_once()


class TestResetEngine:
    """Test suite for reset_engine function."""

    def test_disposes_existing_engine(self):
        """reset_engine disposes existing engine."""
        with patch("db_core.connection.create_engine") as mock_create:
            mock_engine, _ = _create_mock_engine()
            mock_create.return_value = mock_engine

            get_engine()
            reset_engine()

            mock_engine.dispose.assert_called_once()

    def test_resets_engine_to_none(self):
        """reset_engine sets engine to None so next get_engine creates new one."""
        with patch("db_core.connection.create_engine") as mock_create:
            mock_engine, _ = _create_mock_engine()
            mock_create.return_value = mock_engine

            get_engine()
            reset_engine()
            get_engine()

            assert mock_create.call_count == 2

    def test_does_nothing_when_no_engine_exists(self):
        """reset_engine handles case when no engine exists gracefully."""
        # Should not raise
        reset_engine()

    def test_allows_new_engine_creation_after_reset(self):
        """New engine can be created after reset."""
        with patch("db_core.connection.create_engine") as mock_create:
            mock_engine1, _ = _create_mock_engine()
            mock_engine2, _ = _create_mock_engine()

            mock_create.side_effect = [mock_engine1, mock_engine2]

            engine1 = get_engine()
            reset_engine()
            engine2 = get_engine()

            assert engine1 is mock_engine1
            assert engine2 is mock_engine2
            assert engine1 is not engine2
