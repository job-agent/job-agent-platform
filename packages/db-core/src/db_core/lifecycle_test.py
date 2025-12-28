"""Tests for database lifecycle management."""

from unittest.mock import patch, MagicMock

import pytest

from db_core.lifecycle import init_db, drop_all_tables
from db_core.exceptions import DatabaseConnectionError


class TestInitDb:
    """Test suite for init_db function."""

    def test_creates_all_tables_with_default_base_and_engine(self):
        """init_db creates all tables using default Base and engine when not provided."""
        with patch("db_core.lifecycle.get_engine") as mock_get_engine:
            with patch("db_core.lifecycle.Base") as mock_base:
                mock_engine = MagicMock()
                mock_get_engine.return_value = mock_engine
                mock_metadata = MagicMock()
                mock_base.metadata = mock_metadata

                init_db()

                mock_get_engine.assert_called_once()
                mock_metadata.create_all.assert_called_once_with(bind=mock_engine)

    def test_creates_all_tables_with_custom_base(self):
        """init_db accepts custom Base for Alembic isolation."""
        with patch("db_core.lifecycle.get_engine") as mock_get_engine:
            mock_engine = MagicMock()
            mock_get_engine.return_value = mock_engine
            custom_base = MagicMock()
            custom_metadata = MagicMock()
            custom_base.metadata = custom_metadata

            init_db(base=custom_base)

            custom_metadata.create_all.assert_called_once_with(bind=mock_engine)

    def test_creates_all_tables_with_custom_engine(self):
        """init_db accepts custom engine."""
        with patch("db_core.lifecycle.Base") as mock_base:
            custom_engine = MagicMock()
            mock_metadata = MagicMock()
            mock_base.metadata = mock_metadata

            init_db(engine=custom_engine)

            mock_metadata.create_all.assert_called_once_with(bind=custom_engine)

    def test_creates_all_tables_with_custom_base_and_engine(self):
        """init_db accepts both custom Base and custom engine."""
        custom_base = MagicMock()
        custom_metadata = MagicMock()
        custom_base.metadata = custom_metadata
        custom_engine = MagicMock()

        init_db(base=custom_base, engine=custom_engine)

        custom_metadata.create_all.assert_called_once_with(bind=custom_engine)

    def test_raises_database_connection_error_on_failure(self):
        """init_db raises DatabaseConnectionError when initialization fails."""
        with patch("db_core.lifecycle.get_engine") as mock_get_engine:
            mock_get_engine.side_effect = Exception("Connection failed")

            with pytest.raises(DatabaseConnectionError) as exc_info:
                init_db()

            assert "Failed to initialize database" in str(exc_info.value)

    def test_raises_database_connection_error_on_create_all_failure(self):
        """init_db raises DatabaseConnectionError when create_all fails."""
        with patch("db_core.lifecycle.get_engine") as mock_get_engine:
            with patch("db_core.lifecycle.Base") as mock_base:
                mock_engine = MagicMock()
                mock_get_engine.return_value = mock_engine
                mock_metadata = MagicMock()
                mock_metadata.create_all.side_effect = Exception("Failed to create tables")
                mock_base.metadata = mock_metadata

                with pytest.raises(DatabaseConnectionError) as exc_info:
                    init_db()

                assert "Failed to initialize database" in str(exc_info.value)

    def test_preserves_original_exception_as_cause(self):
        """DatabaseConnectionError preserves original exception in chain."""
        with patch("db_core.lifecycle.get_engine") as mock_get_engine:
            original_error = Exception("Original error")
            mock_get_engine.side_effect = original_error

            with pytest.raises(DatabaseConnectionError) as exc_info:
                init_db()

            assert exc_info.value.__cause__ is original_error


class TestDropAllTables:
    """Test suite for drop_all_tables function."""

    def test_drops_all_tables_with_default_base_and_engine(self):
        """drop_all_tables drops all tables using default Base and engine."""
        with patch("db_core.lifecycle.get_engine") as mock_get_engine:
            with patch("db_core.lifecycle.Base") as mock_base:
                mock_engine = MagicMock()
                mock_get_engine.return_value = mock_engine
                mock_metadata = MagicMock()
                mock_base.metadata = mock_metadata

                drop_all_tables()

                mock_get_engine.assert_called_once()
                mock_metadata.drop_all.assert_called_once_with(bind=mock_engine)

    def test_drops_all_tables_with_custom_base(self):
        """drop_all_tables accepts custom Base."""
        with patch("db_core.lifecycle.get_engine") as mock_get_engine:
            mock_engine = MagicMock()
            mock_get_engine.return_value = mock_engine
            custom_base = MagicMock()
            custom_metadata = MagicMock()
            custom_base.metadata = custom_metadata

            drop_all_tables(base=custom_base)

            custom_metadata.drop_all.assert_called_once_with(bind=mock_engine)

    def test_drops_all_tables_with_custom_engine(self):
        """drop_all_tables accepts custom engine."""
        with patch("db_core.lifecycle.Base") as mock_base:
            custom_engine = MagicMock()
            mock_metadata = MagicMock()
            mock_base.metadata = mock_metadata

            drop_all_tables(engine=custom_engine)

            mock_metadata.drop_all.assert_called_once_with(bind=custom_engine)

    def test_drops_all_tables_with_custom_base_and_engine(self):
        """drop_all_tables accepts both custom Base and custom engine."""
        custom_base = MagicMock()
        custom_metadata = MagicMock()
        custom_base.metadata = custom_metadata
        custom_engine = MagicMock()

        drop_all_tables(base=custom_base, engine=custom_engine)

        custom_metadata.drop_all.assert_called_once_with(bind=custom_engine)

    def test_raises_database_connection_error_on_failure(self):
        """drop_all_tables raises DatabaseConnectionError when operation fails."""
        with patch("db_core.lifecycle.get_engine") as mock_get_engine:
            mock_get_engine.side_effect = Exception("Connection failed")

            with pytest.raises(DatabaseConnectionError) as exc_info:
                drop_all_tables()

            assert "Failed to drop tables" in str(exc_info.value)

    def test_raises_database_connection_error_on_drop_all_failure(self):
        """drop_all_tables raises DatabaseConnectionError when drop_all fails."""
        with patch("db_core.lifecycle.get_engine") as mock_get_engine:
            with patch("db_core.lifecycle.Base") as mock_base:
                mock_engine = MagicMock()
                mock_get_engine.return_value = mock_engine
                mock_metadata = MagicMock()
                mock_metadata.drop_all.side_effect = Exception("Failed to drop tables")
                mock_base.metadata = mock_metadata

                with pytest.raises(DatabaseConnectionError) as exc_info:
                    drop_all_tables()

                assert "Failed to drop tables" in str(exc_info.value)

    def test_preserves_original_exception_as_cause(self):
        """DatabaseConnectionError preserves original exception in chain."""
        with patch("db_core.lifecycle.get_engine") as mock_get_engine:
            original_error = Exception("Original error")
            mock_get_engine.side_effect = original_error

            with pytest.raises(DatabaseConnectionError) as exc_info:
                drop_all_tables()

            assert exc_info.value.__cause__ is original_error


class TestLifecycleIntegration:
    """Test integration between init_db and drop_all_tables."""

    def test_init_and_drop_use_same_base_by_default(self):
        """init_db and drop_all_tables use the same default Base."""
        with patch("db_core.lifecycle.get_engine") as mock_get_engine:
            with patch("db_core.lifecycle.Base") as mock_base:
                mock_engine = MagicMock()
                mock_get_engine.return_value = mock_engine
                mock_metadata = MagicMock()
                mock_base.metadata = mock_metadata

                init_db()
                drop_all_tables()

                # Both should use the same Base.metadata
                assert mock_metadata.create_all.call_count == 1
                assert mock_metadata.drop_all.call_count == 1

    def test_different_bases_have_independent_operations(self):
        """Different Base instances operate on different metadata."""
        with patch("db_core.lifecycle.get_engine") as mock_get_engine:
            mock_engine = MagicMock()
            mock_get_engine.return_value = mock_engine

            base1 = MagicMock()
            metadata1 = MagicMock()
            base1.metadata = metadata1

            base2 = MagicMock()
            metadata2 = MagicMock()
            base2.metadata = metadata2

            init_db(base=base1)
            drop_all_tables(base=base2)

            metadata1.create_all.assert_called_once()
            metadata2.drop_all.assert_called_once()
            # Each metadata should only have its operation called
            metadata1.drop_all.assert_not_called()
            metadata2.create_all.assert_not_called()
