"""add_is_relevant_to_jobs

Revision ID: f8e2a1b3c4d5
Revises: 5575254ee36a
Create Date: 2025-12-13 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "f8e2a1b3c4d5"
down_revision: Union[str, None] = "5575254ee36a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add is_relevant column to jobs table.

    - Column is non-nullable with server default True
    - Existing jobs are set to is_relevant=True (backwards compatibility)
    - Index added for query performance when filtering by relevance
    """
    op.add_column(
        "jobs",
        sa.Column(
            "is_relevant",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        schema="jobs",
    )
    op.create_index(
        "ix_jobs_is_relevant",
        "jobs",
        ["is_relevant"],
        unique=False,
        schema="jobs",
    )


def downgrade() -> None:
    """Remove is_relevant column from jobs table."""
    op.drop_index("ix_jobs_is_relevant", table_name="jobs", schema="jobs")
    op.drop_column("jobs", "is_relevant", schema="jobs")
