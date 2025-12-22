"""Tests for db-core package exports."""


class TestDbCoreExports:
    """Test that all required symbols are exported from db_core package."""

    def test_database_config_is_exported(self):
        """DatabaseConfig is exported from db_core."""
        from db_core import DatabaseConfig

        assert DatabaseConfig is not None

    def test_get_database_config_is_exported(self):
        """get_database_config is exported from db_core."""
        from db_core import get_database_config

        assert callable(get_database_config)

    def test_get_engine_is_exported(self):
        """get_engine is exported from db_core."""
        from db_core import get_engine

        assert callable(get_engine)

    def test_reset_engine_is_exported(self):
        """reset_engine is exported from db_core."""
        from db_core import reset_engine

        assert callable(reset_engine)

    def test_get_session_factory_is_exported(self):
        """get_session_factory is exported from db_core."""
        from db_core import get_session_factory

        assert callable(get_session_factory)

    def test_reset_session_factory_is_exported(self):
        """reset_session_factory is exported from db_core."""
        from db_core import reset_session_factory

        assert callable(reset_session_factory)

    def test_get_db_session_is_exported(self):
        """get_db_session is exported from db_core."""
        from db_core import get_db_session

        assert callable(get_db_session)

    def test_transaction_is_exported(self):
        """transaction is exported from db_core."""
        from db_core import transaction

        assert callable(transaction)

    def test_init_db_is_exported(self):
        """init_db is exported from db_core."""
        from db_core import init_db

        assert callable(init_db)

    def test_drop_all_tables_is_exported(self):
        """drop_all_tables is exported from db_core."""
        from db_core import drop_all_tables

        assert callable(drop_all_tables)

    def test_base_is_exported(self):
        """Base is exported from db_core."""
        from db_core import Base

        assert Base is not None

    def test_database_connection_error_is_exported(self):
        """DatabaseConnectionError is exported from db_core."""
        from db_core import DatabaseConnectionError

        assert issubclass(DatabaseConnectionError, Exception)

    def test_transaction_error_is_exported(self):
        """TransactionError is exported from db_core."""
        from db_core import TransactionError

        assert issubclass(TransactionError, Exception)

    def test_base_repository_is_exported(self):
        """BaseRepository is exported from db_core."""
        from db_core import BaseRepository

        assert BaseRepository is not None


class TestDbCoreAllVariable:
    """Test that __all__ includes all required exports."""

    def test_all_variable_exists(self):
        """db_core should have __all__ defined."""
        import db_core

        assert hasattr(db_core, "__all__")

    def test_all_contains_config_exports(self):
        """__all__ includes config-related exports."""
        from db_core import __all__

        assert "DatabaseConfig" in __all__
        assert "get_database_config" in __all__

    def test_all_contains_connection_exports(self):
        """__all__ includes connection-related exports."""
        from db_core import __all__

        assert "get_engine" in __all__
        assert "reset_engine" in __all__

    def test_all_contains_session_exports(self):
        """__all__ includes session-related exports."""
        from db_core import __all__

        assert "get_session_factory" in __all__
        assert "reset_session_factory" in __all__
        assert "get_db_session" in __all__
        assert "transaction" in __all__

    def test_all_contains_lifecycle_exports(self):
        """__all__ includes lifecycle-related exports."""
        from db_core import __all__

        assert "init_db" in __all__
        assert "drop_all_tables" in __all__

    def test_all_contains_base_exports(self):
        """__all__ includes Base export."""
        from db_core import __all__

        assert "Base" in __all__

    def test_all_contains_exception_exports(self):
        """__all__ includes exception exports."""
        from db_core import __all__

        assert "DatabaseConnectionError" in __all__
        assert "TransactionError" in __all__

    def test_all_contains_repository_exports(self):
        """__all__ includes repository exports."""
        from db_core import __all__

        assert "BaseRepository" in __all__


class TestDbCoreSubmoduleImports:
    """Test that submodules can be imported directly."""

    def test_config_module_importable(self):
        """db_core.config can be imported."""
        from db_core import config

        assert hasattr(config, "DatabaseConfig")
        assert hasattr(config, "get_database_config")

    def test_connection_module_importable(self):
        """db_core.connection can be imported."""
        from db_core import connection

        assert hasattr(connection, "get_engine")
        assert hasattr(connection, "reset_engine")

    def test_session_module_importable(self):
        """db_core.session can be imported."""
        from db_core import session

        assert hasattr(session, "get_session_factory")
        assert hasattr(session, "get_db_session")
        assert hasattr(session, "transaction")

    def test_lifecycle_module_importable(self):
        """db_core.lifecycle can be imported."""
        from db_core import lifecycle

        assert hasattr(lifecycle, "init_db")
        assert hasattr(lifecycle, "drop_all_tables")

    def test_base_module_importable(self):
        """db_core.base can be imported."""
        from db_core import base

        assert hasattr(base, "Base")

    def test_exceptions_module_importable(self):
        """db_core.exceptions can be imported."""
        from db_core import exceptions

        assert hasattr(exceptions, "DatabaseError")
        assert hasattr(exceptions, "DatabaseConnectionError")
        assert hasattr(exceptions, "TransactionError")

    def test_repository_package_importable(self):
        """db_core.repository can be imported."""
        from db_core import repository

        assert hasattr(repository, "BaseRepository")
