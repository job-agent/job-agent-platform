"""add_index_on_source_url

Revision ID: 5575254ee36a
Revises: a361684797bf
Create Date: 2025-11-11 15:55:30.213977

"""
from typing import Sequence, Union

from alembic import op


revision: str = '5575254ee36a'
down_revision: Union[str, None] = 'a361684797bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add index on source_url and source columns for URL-based deduplication."""
    op.create_index(
        "ix_jobs_source_url_source",
        "jobs",
        ["source_url", "source"],
        unique=False,
        schema="jobs",
    )


def downgrade() -> None:
    """Remove index on source_url and source columns."""
    op.drop_index("ix_jobs_source_url_source", table_name="jobs", schema="jobs")
