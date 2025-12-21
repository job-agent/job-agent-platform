"""Repository implementation for essay persistence.

This module provides the EssayRepository class that implements
the IEssayRepository interface for CRUD operations on essays.
"""

from contextlib import contextmanager
from typing import Callable, Generator, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select

from job_agent_platform_contracts.essay_repository import IEssayRepository
from job_agent_platform_contracts.essay_repository.schemas import (
    EssayCreate,
    EssayUpdate,
    Essay as EssaySchema,
)
from job_agent_platform_contracts.essay_repository.exceptions import EssayValidationError
from job_agent_platform_contracts.job_repository.exceptions import TransactionError

from essay_repository.models import Essay
from essay_repository.database.session import get_session_factory


class EssayRepository(IEssayRepository):
    """Repository that persists essays to the database.

    The repository supports creating, reading, updating, and deleting
    essay records. It follows the session scope pattern for transaction
    management.
    """

    def __init__(
        self,
        session: Optional[Session] = None,
        session_factory: Optional[Callable[[], Session]] = None,
    ):
        """
        Initialize the repository with a managed or external session.

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
        """Context manager for session lifecycle.

        Args:
            commit: Whether to commit the transaction on success

        Yields:
            SQLAlchemy Session instance
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

    def _model_to_schema(self, essay: Essay) -> EssaySchema:
        """Convert Essay model to Essay schema.

        Args:
            essay: Essay model instance

        Returns:
            Essay Pydantic schema instance
        """
        return EssaySchema.model_validate(essay)

    def create(self, essay_data: EssayCreate) -> EssaySchema:
        """
        Create a new essay from EssayCreate data.

        Args:
            essay_data: Dictionary containing essay fields

        Returns:
            Created Essay schema instance

        Raises:
            EssayValidationError: If data validation fails (e.g., missing answer)
            TransactionError: If database transaction fails
        """
        # Validate required fields
        if "answer" not in essay_data:
            raise EssayValidationError("answer", "Answer is required")

        try:
            with self._session_scope(commit=True) as session:
                essay = Essay(
                    question=essay_data.get("question"),
                    answer=essay_data["answer"],
                    keywords=essay_data.get("keywords"),
                )
                session.add(essay)
                session.flush()

                # Re-query to ensure all fields are loaded
                stmt = select(Essay).where(Essay.id == essay.id)
                essay = session.scalar(stmt)

                if self._close_session:
                    session.expunge(essay)

                return self._model_to_schema(essay)

        except EssayValidationError:
            raise
        except IntegrityError as e:
            raise EssayValidationError("data", f"Integrity constraint violated: {e}") from e
        except SQLAlchemyError as e:
            raise TransactionError(f"Failed to create essay: {e}") from e

    def get_by_id(self, essay_id: int) -> Optional[EssaySchema]:
        """
        Get essay by ID.

        Args:
            essay_id: The essay's primary key identifier

        Returns:
            Essay schema if found, None otherwise
        """
        if essay_id <= 0:
            return None

        with self._session_scope(commit=False) as session:
            stmt = select(Essay).where(Essay.id == essay_id)
            essay = session.scalar(stmt)

            if essay is None:
                return None

            if self._close_session:
                session.expunge(essay)

            return self._model_to_schema(essay)

    def get_all(self) -> List[EssaySchema]:
        """
        Get all essays.

        Returns:
            List of Essay schema instances (may be empty)
        """
        with self._session_scope(commit=False) as session:
            stmt = select(Essay)
            essays = session.scalars(stmt).all()

            if self._close_session:
                for essay in essays:
                    session.expunge(essay)

            return [self._model_to_schema(essay) for essay in essays]

    def delete(self, essay_id: int) -> bool:
        """
        Delete an essay by ID.

        Args:
            essay_id: The essay's primary key identifier

        Returns:
            True if deleted, False if not found
        """
        if essay_id <= 0:
            return False

        try:
            with self._session_scope(commit=True) as session:
                stmt = select(Essay).where(Essay.id == essay_id)
                essay = session.scalar(stmt)

                if essay is None:
                    return False

                session.delete(essay)
                return True

        except SQLAlchemyError as e:
            raise TransactionError(f"Failed to delete essay: {e}") from e

    def update(self, essay_id: int, essay_data: EssayUpdate) -> Optional[EssaySchema]:
        """
        Update an existing essay.

        Args:
            essay_id: The essay's primary key identifier
            essay_data: Dictionary with fields to update

        Returns:
            Updated Essay schema if found, None if not found

        Raises:
            EssayValidationError: If data validation fails
            TransactionError: If database transaction fails
        """
        if essay_id <= 0:
            return None

        try:
            with self._session_scope(commit=True) as session:
                stmt = select(Essay).where(Essay.id == essay_id)
                essay = session.scalar(stmt)

                if essay is None:
                    return None

                # Update only provided fields
                if "question" in essay_data:
                    essay.question = essay_data["question"]
                if "answer" in essay_data:
                    essay.answer = essay_data["answer"]
                if "keywords" in essay_data:
                    essay.keywords = essay_data["keywords"]

                session.flush()

                # Re-query to get updated timestamps
                session.refresh(essay)

                if self._close_session:
                    session.expunge(essay)

                return self._model_to_schema(essay)

        except IntegrityError as e:
            raise EssayValidationError("data", f"Integrity constraint violated: {e}") from e
        except SQLAlchemyError as e:
            raise TransactionError(f"Failed to update essay: {e}") from e
