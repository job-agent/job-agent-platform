"""Essay model."""

from datetime import datetime, UTC
from typing import Any, Optional

from sqlalchemy import Float, Text
from sqlalchemy.dialects.postgresql import ARRAY, VARCHAR, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from essay_repository.models.base import Base


class Essay(Base):
    """Essay entity model."""

    __tablename__ = "essays"
    __table_args__ = {"schema": "essays"}

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)

    question: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    keywords: Mapped[Optional[list[str]]] = mapped_column(ARRAY(VARCHAR), nullable=True)
    embedding: Mapped[Optional[list[float]]] = mapped_column(ARRAY(Float), nullable=True)
    search_vector: Mapped[Optional[Any]] = mapped_column(TSVECTOR, nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __repr__(self) -> str:
        """String representation of Essay."""
        question_preview = (
            self.question[:30] + "..."
            if self.question and len(self.question) > 30
            else self.question
        )
        return f"<Essay(id={self.id}, question='{question_preview}')>"
