"""Tests for BaseRepository class."""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from db_core.repository.base import BaseRepository


class TestBaseRepositoryInit:
    """Test suite for BaseRepository initialization."""

    def test_init_with_session_sets_close_session_false(self):
        """When initialized with session, _close_session is False."""
        mock_session = MagicMock(spec=Session)

        repo = BaseRepository(session=mock_session)

        assert repo._close_session is False

    def test_init_with_session_factory_sets_close_session_true(self):
        """When initialized with session_factory, _close_session is True."""
        mock_factory = MagicMock()
        mock_factory.return_value = MagicMock(spec=Session)

        repo = BaseRepository(session_factory=mock_factory)

        assert repo._close_session is True

    def test_init_with_neither_uses_default_factory(self):
        """When initialized with neither, uses get_session_factory default."""
        with patch("db_core.repository.base.get_session_factory") as mock_get_factory:
            mock_factory = MagicMock()
            mock_get_factory.return_value = mock_factory

            repo = BaseRepository()

            mock_get_factory.assert_called_once()
            assert repo._close_session is True

    def test_init_with_both_raises_value_error(self):
        """Providing both session and session_factory raises ValueError."""
        mock_session = MagicMock(spec=Session)
        mock_factory = MagicMock()

        with pytest.raises(ValueError) as exc_info:
            BaseRepository(session=mock_session, session_factory=mock_factory)

        assert "either session or session_factory" in str(exc_info.value).lower()

    def test_init_with_non_callable_factory_raises_type_error(self):
        """Providing non-callable session_factory raises TypeError."""
        with pytest.raises(TypeError) as exc_info:
            BaseRepository(session_factory="not_callable")

        assert "callable" in str(exc_info.value).lower()

    def test_init_with_session_wraps_in_lambda(self):
        """When session is provided, it's wrapped so _session_factory returns it."""
        mock_session = MagicMock(spec=Session)

        repo = BaseRepository(session=mock_session)

        # The factory should return the same session
        assert repo._session_factory() is mock_session


class TestBaseRepositorySessionScope:
    """Test suite for BaseRepository._session_scope context manager."""

    def test_session_scope_yields_session(self):
        """_session_scope yields a session from the factory."""
        mock_session = MagicMock(spec=Session)
        mock_factory = MagicMock(return_value=mock_session)

        repo = BaseRepository(session_factory=mock_factory)

        with repo._session_scope(commit=False) as session:
            assert session is mock_session

    def test_session_scope_commits_when_commit_true(self):
        """_session_scope commits the session when commit=True."""
        mock_session = MagicMock(spec=Session)
        mock_factory = MagicMock(return_value=mock_session)

        repo = BaseRepository(session_factory=mock_factory)

        with repo._session_scope(commit=True):
            pass

        mock_session.commit.assert_called_once()

    def test_session_scope_does_not_commit_when_commit_false(self):
        """_session_scope does not commit when commit=False."""
        mock_session = MagicMock(spec=Session)
        mock_factory = MagicMock(return_value=mock_session)

        repo = BaseRepository(session_factory=mock_factory)

        with repo._session_scope(commit=False):
            pass

        mock_session.commit.assert_not_called()

    def test_session_scope_rolls_back_on_exception(self):
        """_session_scope rolls back on exception."""
        mock_session = MagicMock(spec=Session)
        mock_factory = MagicMock(return_value=mock_session)

        repo = BaseRepository(session_factory=mock_factory)

        with pytest.raises(ValueError):
            with repo._session_scope(commit=True):
                raise ValueError("Test error")

        mock_session.rollback.assert_called_once()
        mock_session.commit.assert_not_called()

    def test_session_scope_re_raises_exception(self):
        """_session_scope re-raises the original exception."""
        mock_session = MagicMock(spec=Session)
        mock_factory = MagicMock(return_value=mock_session)

        repo = BaseRepository(session_factory=mock_factory)

        with pytest.raises(ValueError) as exc_info:
            with repo._session_scope(commit=True):
                raise ValueError("Original error message")

        assert "Original error message" in str(exc_info.value)

    def test_session_scope_closes_session_when_close_session_true(self):
        """_session_scope closes session when _close_session is True."""
        mock_session = MagicMock(spec=Session)
        mock_factory = MagicMock(return_value=mock_session)

        repo = BaseRepository(session_factory=mock_factory)
        assert repo._close_session is True

        with repo._session_scope(commit=False):
            pass

        mock_session.close.assert_called_once()

    def test_session_scope_does_not_close_session_when_close_session_false(self):
        """_session_scope does not close session when _close_session is False (external session)."""
        mock_session = MagicMock(spec=Session)

        repo = BaseRepository(session=mock_session)
        assert repo._close_session is False

        with repo._session_scope(commit=False):
            pass

        mock_session.close.assert_not_called()

    def test_session_scope_closes_session_even_on_error(self):
        """_session_scope closes session even when exception occurs."""
        mock_session = MagicMock(spec=Session)
        mock_factory = MagicMock(return_value=mock_session)

        repo = BaseRepository(session_factory=mock_factory)

        try:
            with repo._session_scope(commit=True):
                raise Exception("Test error")
        except Exception:
            pass

        mock_session.close.assert_called_once()

    def test_session_scope_does_not_close_external_session_on_error(self):
        """_session_scope does not close external session even on error."""
        mock_session = MagicMock(spec=Session)

        repo = BaseRepository(session=mock_session)

        try:
            with repo._session_scope(commit=True):
                raise Exception("Test error")
        except Exception:
            pass

        mock_session.close.assert_not_called()


class TestBaseRepositorySessionScopeEdgeCases:
    """Test edge cases for _session_scope."""

    def test_session_scope_with_exception_in_commit(self):
        """_session_scope handles exception during commit."""
        mock_session = MagicMock(spec=Session)
        mock_session.commit.side_effect = Exception("Commit failed")
        mock_factory = MagicMock(return_value=mock_session)

        repo = BaseRepository(session_factory=mock_factory)

        with pytest.raises(Exception) as exc_info:
            with repo._session_scope(commit=True):
                pass

        assert "Commit failed" in str(exc_info.value)
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_session_scope_allows_nested_usage(self):
        """_session_scope can be used in nested manner."""
        mock_session = MagicMock(spec=Session)
        mock_factory = MagicMock(return_value=mock_session)

        repo = BaseRepository(session_factory=mock_factory)

        with repo._session_scope(commit=False):
            with repo._session_scope(commit=False):
                # Each scope creates a new session from factory
                pass

        # Factory called twice for nested scopes
        assert mock_factory.call_count == 2

    def test_session_scope_multiple_sequential_uses(self):
        """_session_scope can be used multiple times sequentially."""
        mock_session = MagicMock(spec=Session)
        mock_factory = MagicMock(return_value=mock_session)

        repo = BaseRepository(session_factory=mock_factory)

        with repo._session_scope(commit=False):
            pass

        with repo._session_scope(commit=True):
            pass

        assert mock_factory.call_count == 2
        assert mock_session.close.call_count == 2


class TestBaseRepositoryInheritance:
    """Test that BaseRepository can be properly inherited."""

    def test_subclass_can_use_session_scope(self):
        """Subclass can use _session_scope from BaseRepository."""

        class ConcreteRepository(BaseRepository):
            def get_data(self):
                with self._session_scope(commit=False):
                    return "data"

        mock_session = MagicMock(spec=Session)
        mock_factory = MagicMock(return_value=mock_session)

        repo = ConcreteRepository(session_factory=mock_factory)
        result = repo.get_data()

        assert result == "data"
        mock_factory.assert_called_once()

    def test_subclass_inherits_init_behavior(self):
        """Subclass inherits __init__ validation behavior."""

        class ConcreteRepository(BaseRepository):
            pass

        mock_session = MagicMock(spec=Session)
        mock_factory = MagicMock()

        with pytest.raises(ValueError):
            ConcreteRepository(session=mock_session, session_factory=mock_factory)

    def test_subclass_can_add_additional_init_params(self):
        """Subclass can add additional __init__ parameters."""

        class ConcreteRepository(BaseRepository):
            def __init__(self, extra_param, **kwargs):
                super().__init__(**kwargs)
                self.extra_param = extra_param

        mock_session = MagicMock(spec=Session)

        repo = ConcreteRepository(extra_param="value", session=mock_session)

        assert repo.extra_param == "value"
        assert repo._close_session is False
