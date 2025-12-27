"""Base repository class with session management.

This module provides the BaseRepository class that repositories can inherit
from to get consistent session management behavior.
"""

from contextlib import contextmanager
from typing import Callable, Generator, Optional

from sqlalchemy.orm import Session

from db_core.session import get_session_factory


class BaseRepository:
    """Base repository with session management.

    Provides a common pattern for repository classes to manage database
    sessions. Supports both managed sessions (from factory) and external
    sessions (passed in by caller).

    Attributes:
        _session_factory: Callable that returns a Session
        _close_session: Whether to close session after use
    """

    def __init__(
        self,
        session: Optional[Session] = None,
        session_factory: Optional[Callable[[], Session]] = None,
    ):
        """Initialize the repository with a managed or external session.

        Args:
            session: Existing SQLAlchemy session to reuse
            session_factory: Callable returning SQLAlchemy session instances

        Raises:
            ValueError: If both session and session_factory are provided
            TypeError: If session_factory is not callable
        """
        if session is not None and session_factory is not None:
            raise ValueError("Provide either session or session_factory, not both")

        if session is not None:
            self._session_factory: Callable[[], Session] = lambda: session
            self._close_session = False
        else:
            factory_candidate = session_factory or get_session_factory()

            if not callable(factory_candidate):
                raise TypeError("session_factory must be callable")

            self._session_factory = lambda: factory_candidate()
            self._close_session = True

    @contextmanager
    def _session_scope(self, *, commit: bool) -> Generator[Session, None, None]:
        """Context manager for database session scope.

        Provides consistent session lifecycle management:
        - Creates session from factory
        - Commits on success if commit=True
        - Rolls back on exception
        - Closes session if using managed sessions

        Args:
            commit: Whether to commit the session on success

        Yields:
            SQLAlchemy Session

        Raises:
            Exception: Re-raises any exception after rollback
        """
        session = self._session_factory()
        close_session = self._close_session

        try:
            yield session
            if commit:
                session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            if close_session:
                session.close()
