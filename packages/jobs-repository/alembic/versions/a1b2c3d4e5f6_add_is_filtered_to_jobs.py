"""add_is_filtered_to_jobs

Revision ID: a1b2c3d4e5f6
Revises: f8e2a1b3c4d5
Create Date: 2025-12-14 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "f8e2a1b3c4d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add is_filtered column to jobs table.

    - Column is non-nullable with server default False
    - Existing jobs are set to is_filtered=False (they passed filtering when stored)
    - Index added for query performance when filtering by is_filtered status
    """
    op.add_column(
        "jobs",
        sa.Column(
            "is_filtered",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        schema="jobs",
    )
    op.create_index(
        "ix_jobs_is_filtered",
        "jobs",
        ["is_filtered"],
        unique=False,
        schema="jobs",
    )


def downgrade() -> None:
    """Remove is_filtered column from jobs table."""
    op.drop_index("ix_jobs_is_filtered", table_name="jobs", schema="jobs")
    op.drop_column("jobs", "is_filtered", schema="jobs")
