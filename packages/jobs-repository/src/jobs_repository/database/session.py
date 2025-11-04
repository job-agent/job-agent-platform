"""Database session management."""

from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from jobs_repository.database.connection import get_engine
from jobs_repository.exceptions import TransactionError


_SessionLocal: Optional[sessionmaker] = None


def get_session_factory() -> sessionmaker:
    """
    Get or create the session factory.

    Returns:
        SQLAlchemy session factory
    """
    global _SessionLocal

    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return _SessionLocal


def get_db_session() -> Generator[Session, None, None]:
    """
    Create and yield a database session.

    Yields:
        Session: SQLAlchemy database session

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
    """
    Context manager for database transactions.

    Automatically commits on success or rolls back on failure.

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


def reset_session_factory() -> None:
    """
    Reset the global session factory.

    Useful for testing or when configuration changes.
    """
    global _SessionLocal
    _SessionLocal = None
