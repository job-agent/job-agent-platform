"""remove_is_active_and_experience_level_add_company_website

Revision ID: 32bbf7298a3a
Revises: 723f0730a321
Create Date: 2025-11-02 19:53:17.646106

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '32bbf7298a3a'
down_revision: Union[str, None] = '723f0730a321'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add website to companies and remove is_active and experience_level from jobs."""

    # Add website column to companies table
    op.add_column("companies", sa.Column("website", sa.String(length=500), nullable=True), schema="jobs")

    # Drop index on is_active if it exists
    connection = op.get_bind()
    result = connection.execute(
        sa.text(
            """
            SELECT indexname FROM pg_indexes
            WHERE schemaname = 'jobs' AND tablename = 'jobs' AND indexname = 'ix_jobs_jobs_is_active'
        """
        )
    ).fetchone()

    if result:
        op.drop_index("ix_jobs_jobs_is_active", table_name="jobs", schema="jobs")

    # Remove columns from jobs table
    op.drop_column("jobs", "is_active", schema="jobs")
    op.drop_column("jobs", "experience_level", schema="jobs")


def downgrade() -> None:
    """Restore is_active and experience_level to jobs and remove website from companies."""

    # Add back columns to jobs table
    op.add_column("jobs", sa.Column("experience_level", sa.String(length=100), nullable=True), schema="jobs")
    op.add_column("jobs", sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("true")), schema="jobs")

    # Recreate index on is_active
    op.create_index("ix_jobs_jobs_is_active", "jobs", ["is_active"], unique=False, schema="jobs")

    # Remove website column from companies table
    op.drop_column("companies", "website", schema="jobs")
