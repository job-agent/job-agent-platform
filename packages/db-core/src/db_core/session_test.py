"""Tests for database session management."""

from unittest.mock import patch, MagicMock
import threading

import pytest
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from db_core.session import (
    get_session_factory,
    get_db_session,
    transaction,
    reset_session_factory,
)
from db_core.exceptions import TransactionError


class TestGetSessionFactory:
    """Test suite for get_session_factory function."""

    def setup_method(self):
        """Reset session factory before each test."""
        reset_session_factory()

    def teardown_method(self):
        """Clean up after each test."""
        reset_session_factory()

    def test_creates_session_factory_on_first_call(self):
        """get_session_factory creates factory on first call."""
        with patch("db_core.session.get_engine") as mock_get_engine:
            mock_engine = MagicMock()
            mock_get_engine.return_value = mock_engine

            factory = get_session_factory()

            assert isinstance(factory, sessionmaker)
            mock_get_engine.assert_called_once()

    def test_reuses_existing_factory_singleton(self):
        """get_session_factory reuses existing factory on subsequent calls."""
        with patch("db_core.session.get_engine") as mock_get_engine:
            mock_engine = MagicMock()
            mock_get_engine.return_value = mock_engine

            factory1 = get_session_factory()
            factory2 = get_session_factory()

            assert factory1 is factory2
            mock_get_engine.assert_called_once()

    def test_factory_creates_sessions(self):
        """Factory can create session instances."""
        with patch("db_core.session.get_engine") as mock_get_engine:
            mock_engine = MagicMock()
            mock_get_engine.return_value = mock_engine

            factory = get_session_factory()
            session = factory()

            assert session is not None

    def test_session_factory_uses_autocommit_false(self):
        """Session factory creates sessions with autocommit=False."""
        with patch("db_core.session.get_engine") as mock_get_engine:
            mock_engine = MagicMock()
            mock_get_engine.return_value = mock_engine

            factory = get_session_factory()

            # sessionmaker stores these in kw
            assert factory.kw.get("autocommit", True) is False

    def test_session_factory_uses_autoflush_false(self):
        """Session factory creates sessions with autoflush=False."""
        with patch("db_core.session.get_engine") as mock_get_engine:
            mock_engine = MagicMock()
            mock_get_engine.return_value = mock_engine

            factory = get_session_factory()

            assert factory.kw.get("autoflush", True) is False


class TestGetSessionFactoryThreadSafety:
    """Test thread safety of get_session_factory."""

    def setup_method(self):
        """Reset session factory before each test."""
        reset_session_factory()

    def teardown_method(self):
        """Clean up after each test."""
        reset_session_factory()

    def test_thread_safe_factory_creation(self):
        """get_session_factory is thread-safe - multiple threads get same factory."""
        with patch("db_core.session.get_engine") as mock_get_engine:
            mock_engine = MagicMock()
            mock_get_engine.return_value = mock_engine

            factories = []
            errors = []

            def get_factory_thread():
                try:
                    factory = get_session_factory()
                    factories.append(factory)
                except Exception as e:
                    errors.append(e)

            threads = [threading.Thread(target=get_factory_thread) for _ in range(10)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            assert len(errors) == 0
            assert len(factories) == 10
            assert all(f is factories[0] for f in factories)
            mock_get_engine.assert_called_once()


class TestResetSessionFactory:
    """Test suite for reset_session_factory function."""

    def teardown_method(self):
        """Clean up after each test."""
        reset_session_factory()

    def test_resets_factory_to_none(self):
        """reset_session_factory sets factory to None."""
        with patch("db_core.session.get_engine") as mock_get_engine:
            mock_engine = MagicMock()
            mock_get_engine.return_value = mock_engine

            get_session_factory()
            reset_session_factory()
            get_session_factory()

            assert mock_get_engine.call_count == 2

    def test_allows_new_factory_creation_after_reset(self):
        """New factory can be created after reset."""
        with patch("db_core.session.get_engine") as mock_get_engine:
            mock_engine = MagicMock()
            mock_get_engine.return_value = mock_engine

            factory1 = get_session_factory()
            reset_session_factory()
            factory2 = get_session_factory()

            assert factory1 is not factory2


class TestGetDbSession:
    """Test suite for get_db_session generator."""

    def setup_method(self):
        """Reset session factory before each test."""
        reset_session_factory()

    def teardown_method(self):
        """Clean up after each test."""
        reset_session_factory()

    def test_yields_session(self):
        """get_db_session yields a session."""
        with patch("db_core.session.get_session_factory") as mock_factory:
            mock_session = MagicMock(spec=Session)
            mock_factory.return_value = MagicMock(return_value=mock_session)

            session_gen = get_db_session()
            session = next(session_gen)

            assert session is mock_session

    def test_closes_session_after_use(self):
        """get_db_session closes session after normal completion."""
        with patch("db_core.session.get_session_factory") as mock_factory:
            mock_session = MagicMock(spec=Session)
            mock_factory.return_value = MagicMock(return_value=mock_session)

            session_gen = get_db_session()
            _ = next(session_gen)

            try:
                next(session_gen)
            except StopIteration:
                pass

            mock_session.close.assert_called_once()

    def test_rolls_back_on_sqlalchemy_error(self):
        """get_db_session rolls back on SQLAlchemyError."""
        with patch("db_core.session.get_session_factory") as mock_factory:
            mock_session = MagicMock(spec=Session)
            mock_factory.return_value = MagicMock(return_value=mock_session)

            session_gen = get_db_session()
            _ = next(session_gen)

            with pytest.raises(TransactionError):
                session_gen.throw(SQLAlchemyError("Test error"))

            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()

    def test_raises_transaction_error_on_sqlalchemy_error(self):
        """get_db_session raises TransactionError on SQLAlchemyError."""
        with patch("db_core.session.get_session_factory") as mock_factory:
            mock_session = MagicMock(spec=Session)
            mock_factory.return_value = MagicMock(return_value=mock_session)

            session_gen = get_db_session()
            next(session_gen)

            with pytest.raises(TransactionError) as exc_info:
                session_gen.throw(SQLAlchemyError("Database error"))

            assert "Database operation failed" in str(exc_info.value)

    def test_closes_session_even_on_error(self):
        """Session is closed even when error occurs."""
        with patch("db_core.session.get_session_factory") as mock_factory:
            mock_session = MagicMock(spec=Session)
            mock_factory.return_value = MagicMock(return_value=mock_session)

            session_gen = get_db_session()
            next(session_gen)

            try:
                session_gen.throw(SQLAlchemyError("Test error"))
            except TransactionError:
                pass

            mock_session.close.assert_called_once()


class TestTransaction:
    """Test suite for transaction context manager."""

    def setup_method(self):
        """Reset session factory before each test."""
        reset_session_factory()

    def teardown_method(self):
        """Clean up after each test."""
        reset_session_factory()

    def test_yields_session(self):
        """transaction yields a session."""
        with patch("db_core.session.get_session_factory") as mock_factory:
            mock_session = MagicMock(spec=Session)
            mock_factory.return_value = MagicMock(return_value=mock_session)

            with transaction() as session:
                assert session is mock_session

    def test_commits_on_success(self):
        """transaction commits on successful completion."""
        with patch("db_core.session.get_session_factory") as mock_factory:
            mock_session = MagicMock(spec=Session)
            mock_factory.return_value = MagicMock(return_value=mock_session)

            with transaction() as _:
                pass

            mock_session.commit.assert_called_once()

    def test_closes_session_after_commit(self):
        """transaction closes session after commit."""
        with patch("db_core.session.get_session_factory") as mock_factory:
            mock_session = MagicMock(spec=Session)
            mock_factory.return_value = MagicMock(return_value=mock_session)

            with transaction() as _:
                pass

            mock_session.close.assert_called_once()

    def test_rolls_back_on_exception(self):
        """transaction rolls back on exception."""
        with patch("db_core.session.get_session_factory") as mock_factory:
            mock_session = MagicMock(spec=Session)
            mock_factory.return_value = MagicMock(return_value=mock_session)

            with pytest.raises(TransactionError):
                with transaction() as _:
                    raise Exception("Test error")

            mock_session.rollback.assert_called_once()
            mock_session.commit.assert_not_called()

    def test_raises_transaction_error_on_exception(self):
        """transaction raises TransactionError on exception."""
        with patch("db_core.session.get_session_factory") as mock_factory:
            mock_session = MagicMock(spec=Session)
            mock_factory.return_value = MagicMock(return_value=mock_session)

            with pytest.raises(TransactionError) as exc_info:
                with transaction() as _:
                    raise ValueError("Test error")

            assert "Transaction failed" in str(exc_info.value)

    def test_closes_session_even_on_error(self):
        """Session is closed even when error occurs."""
        with patch("db_core.session.get_session_factory") as mock_factory:
            mock_session = MagicMock(spec=Session)
            mock_factory.return_value = MagicMock(return_value=mock_session)

            try:
                with transaction() as _:
                    raise Exception("Test error")
            except TransactionError:
                pass

            mock_session.close.assert_called_once()

    def test_does_not_commit_on_rollback(self):
        """transaction does not commit after rollback."""
        with patch("db_core.session.get_session_factory") as mock_factory:
            mock_session = MagicMock(spec=Session)
            mock_factory.return_value = MagicMock(return_value=mock_session)

            try:
                with transaction() as _:
                    raise Exception("Force rollback")
            except TransactionError:
                pass

            mock_session.commit.assert_not_called()
            mock_session.rollback.assert_called_once()

    def test_handles_sqlalchemy_error(self):
        """transaction handles SQLAlchemyError."""
        with patch("db_core.session.get_session_factory") as mock_factory:
            mock_session = MagicMock(spec=Session)
            mock_factory.return_value = MagicMock(return_value=mock_session)

            with pytest.raises(TransactionError):
                with transaction() as _:
                    raise SQLAlchemyError("Database error")

            mock_session.rollback.assert_called_once()

    def test_preserves_original_exception_as_cause(self):
        """TransactionError preserves original exception in chain."""
        with patch("db_core.session.get_session_factory") as mock_factory:
            mock_session = MagicMock(spec=Session)
            mock_factory.return_value = MagicMock(return_value=mock_session)

            original_error = ValueError("original error")

            with pytest.raises(TransactionError) as exc_info:
                with transaction() as _:
                    raise original_error

            assert exc_info.value.__cause__ is original_error
