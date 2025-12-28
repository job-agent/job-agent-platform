"""Database session management.

This module provides thread-safe session management:
- get_session_factory: Get or create singleton session factory
- reset_session_factory: Reset the global session factory
- get_db_session: Generator yielding database sessions
- transaction: Context manager for database transactions
"""

import threading
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from db_core.connection import get_engine
from db_core.exceptions import TransactionError


_SessionLocal: Optional[sessionmaker] = None
_session_lock = threading.Lock()


def get_session_factory() -> sessionmaker:
    """Get or create the session factory.

    Creates a singleton session factory with thread-safe initialization.
    Sessions are configured with autocommit=False and autoflush=False.

    Returns:
        SQLAlchemy session factory
    """
    global _SessionLocal

    if _SessionLocal is not None:
        return _SessionLocal

    with _session_lock:
        if _SessionLocal is None:
            engine = get_engine()
            _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return _SessionLocal


def reset_session_factory() -> None:
    """Reset the global session factory.

    Resets the session factory to None. Useful for testing or when
    configuration changes.
    """
    global _SessionLocal
    with _session_lock:
        _SessionLocal = None


def get_db_session() -> Generator[Session, None, None]:
    """Create and yield a database session.

    Yields:
        Session: SQLAlchemy database session

    Raises:
        TransactionError: If a SQLAlchemyError occurs during session usage

    Example:
        >>> session = next(get_db_session())
        >>> try:
        ...     pass
        ... finally:
        ...     session.close()
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        raise TransactionError(f"Database operation failed: {e}") from e
    finally:
        db.close()


@contextmanager
def transaction() -> Generator[Session, None, None]:
    """Context manager for database transactions.

    Automatically commits on success or rolls back on failure.
    Session is always closed after use.

    Yields:
        Session: SQLAlchemy database session

    Raises:
        TransactionError: If transaction fails

    Example:
        >>> with transaction() as session:
        ...     job = Job(title="Software Engineer")
        ...     session.add(job)
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise TransactionError(f"Transaction failed: {e}") from e
    finally:
        session.close()
