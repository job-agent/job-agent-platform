"""Tests for database lifecycle management."""

from unittest.mock import patch, MagicMock

import pytest

from jobs_repository.database.lifecycle import init_db, drop_all_tables
from job_agent_platform_contracts.job_repository.exceptions import DatabaseConnectionError


class TestInitDb:
    """Test suite for init_db function."""

    def test_creates_all_tables(self):
        """Test that init_db creates all tables."""
        with patch("jobs_repository.database.lifecycle.get_engine") as mock_get_engine:
            with patch("jobs_repository.database.lifecycle.Base") as mock_base:
                mock_engine = MagicMock()
                mock_get_engine.return_value = mock_engine
                mock_metadata = MagicMock()
                mock_base.metadata = mock_metadata

                init_db()

                mock_get_engine.assert_called_once()
                mock_metadata.create_all.assert_called_once_with(bind=mock_engine)

    def test_uses_correct_engine(self):
        """Test that init_db uses engine from get_engine."""
        with patch("jobs_repository.database.lifecycle.get_engine") as mock_get_engine:
            with patch("jobs_repository.database.lifecycle.Base") as mock_base:
                mock_engine = MagicMock()
                mock_get_engine.return_value = mock_engine
                mock_metadata = MagicMock()
                mock_base.metadata = mock_metadata

                init_db()

                mock_metadata.create_all.assert_called_with(bind=mock_engine)

    def test_raises_database_connection_error_on_failure(self):
        """Test that init_db raises DatabaseConnectionError on failure."""
        with patch("jobs_repository.database.lifecycle.get_engine") as mock_get_engine:
            mock_get_engine.side_effect = Exception("Connection failed")

            with pytest.raises(DatabaseConnectionError) as exc_info:
                init_db()

            assert "Failed to initialize database" in str(exc_info.value)

    def test_raises_error_on_create_all_failure(self):
        """Test that init_db raises error when create_all fails."""
        with patch("jobs_repository.database.lifecycle.get_engine") as mock_get_engine:
            with patch("jobs_repository.database.lifecycle.Base") as mock_base:
                mock_engine = MagicMock()
                mock_get_engine.return_value = mock_engine
                mock_metadata = MagicMock()
                mock_metadata.create_all.side_effect = Exception("Create failed")
                mock_base.metadata = mock_metadata

                with pytest.raises(DatabaseConnectionError) as exc_info:
                    init_db()

                assert "Failed to initialize database" in str(exc_info.value)

    def test_propagates_original_exception(self):
        """Test that init_db preserves original exception as cause."""
        with patch("jobs_repository.database.lifecycle.get_engine") as mock_get_engine:
            original_error = Exception("Original error")
            mock_get_engine.side_effect = original_error

            with pytest.raises(DatabaseConnectionError) as exc_info:
                init_db()

            assert exc_info.value.__cause__ is original_error


class TestDropAllTables:
    """Test suite for drop_all_tables function."""

    def test_drops_all_tables(self):
        """Test that drop_all_tables drops all tables."""
        with patch("jobs_repository.database.lifecycle.get_engine") as mock_get_engine:
            with patch("jobs_repository.database.lifecycle.Base") as mock_base:
                mock_engine = MagicMock()
                mock_get_engine.return_value = mock_engine
                mock_metadata = MagicMock()
                mock_base.metadata = mock_metadata

                drop_all_tables()

                mock_get_engine.assert_called_once()
                mock_metadata.drop_all.assert_called_once_with(bind=mock_engine)

    def test_uses_correct_engine(self):
        """Test that drop_all_tables uses engine from get_engine."""
        with patch("jobs_repository.database.lifecycle.get_engine") as mock_get_engine:
            with patch("jobs_repository.database.lifecycle.Base") as mock_base:
                mock_engine = MagicMock()
                mock_get_engine.return_value = mock_engine
                mock_metadata = MagicMock()
                mock_base.metadata = mock_metadata

                drop_all_tables()

                mock_metadata.drop_all.assert_called_with(bind=mock_engine)

    def test_raises_database_connection_error_on_failure(self):
        """Test that drop_all_tables raises DatabaseConnectionError on failure."""
        with patch("jobs_repository.database.lifecycle.get_engine") as mock_get_engine:
            mock_get_engine.side_effect = Exception("Connection failed")

            with pytest.raises(DatabaseConnectionError) as exc_info:
                drop_all_tables()

            assert "Failed to drop tables" in str(exc_info.value)

    def test_raises_error_on_drop_all_failure(self):
        """Test that drop_all_tables raises error when drop_all fails."""
        with patch("jobs_repository.database.lifecycle.get_engine") as mock_get_engine:
            with patch("jobs_repository.database.lifecycle.Base") as mock_base:
                mock_engine = MagicMock()
                mock_get_engine.return_value = mock_engine
                mock_metadata = MagicMock()
                mock_metadata.drop_all.side_effect = Exception("Drop failed")
                mock_base.metadata = mock_metadata

                with pytest.raises(DatabaseConnectionError) as exc_info:
                    drop_all_tables()

                assert "Failed to drop tables" in str(exc_info.value)

    def test_propagates_original_exception(self):
        """Test that drop_all_tables preserves original exception as cause."""
        with patch("jobs_repository.database.lifecycle.get_engine") as mock_get_engine:
            original_error = Exception("Original error")
            mock_get_engine.side_effect = original_error

            with pytest.raises(DatabaseConnectionError) as exc_info:
                drop_all_tables()

            assert exc_info.value.__cause__ is original_error
