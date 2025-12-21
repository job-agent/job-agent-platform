"""Essay model."""

from datetime import datetime, UTC

from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.dialects.postgresql import ARRAY, VARCHAR

from essay_repository.models.base import Base


class Essay(Base):
    """Essay entity model."""

    __tablename__ = "essays"
    __table_args__ = {"schema": "essays"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    question = Column(Text, nullable=True)
    answer = Column(Text, nullable=False)
    keywords = Column(ARRAY(VARCHAR), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
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
