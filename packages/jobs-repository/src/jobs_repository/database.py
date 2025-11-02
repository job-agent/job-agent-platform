"""Database connection and session management."""

import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/jobs")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,  # Connection pool size
    max_overflow=20,  # Maximum overflow connections
    echo=False,  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base for models
Base = declarative_base()


def get_db_session() -> Generator[Session, None, None]:
    """
    Create and yield a database session.

    Yields:
        Session: SQLAlchemy database session

    Example:
        >>> session = next(get_db_session())
        >>> try:
        ...     # Use session
        ...     pass
        ... finally:
        ...     session.close()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize the database by creating all tables.

    This should be called once when setting up the database.
    For production, use Alembic migrations instead.
    """
    Base.metadata.create_all(bind=engine)


def drop_all_tables() -> None:
    """
    Drop all tables from the database.

    WARNING: This will delete all data. Use with caution!
    Only intended for development/testing.
    """
    Base.metadata.drop_all(bind=engine)
