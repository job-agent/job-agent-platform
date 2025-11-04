"""remove_legacy_columns_from_jobs

Revision ID: 9313e7f4c4bb
Revises: 5d2bab6f2e10
Create Date: 2025-11-02 16:49:16.689444

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "9313e7f4c4bb"
down_revision: Union[str, None] = "5d2bab6f2e10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove legacy columns from jobs table."""

    connection = op.get_bind()

    result = connection.execute(
        sa.text(
            """
        SELECT indexname FROM pg_indexes
        WHERE schemaname = 'jobs' AND tablename = 'jobs' AND indexname = 'ix_jobs_jobs_company'
    """
        )
    ).fetchone()

    if result:
        op.drop_index("ix_jobs_jobs_company", table_name="jobs", schema="jobs")

    op.drop_column("jobs", "company", schema="jobs")
    op.drop_column("jobs", "location", schema="jobs")
    op.drop_column("jobs", "extra_data", schema="jobs")


def downgrade() -> None:
    """Restore legacy columns to jobs table."""

    op.add_column("jobs", sa.Column("company", sa.String(length=300), nullable=True), schema="jobs")
    op.add_column(
        "jobs", sa.Column("location", sa.String(length=300), nullable=True), schema="jobs"
    )
    op.add_column(
        "jobs",
        sa.Column("extra_data", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        schema="jobs",
    )

    op.create_index("ix_jobs_jobs_company", "jobs", ["company"], unique=False, schema="jobs")

    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
        UPDATE jobs.jobs j
        SET company = c.name
        FROM jobs.companies c
        WHERE j.company_id = c.id
    """
        )
    )

    connection.execute(
        sa.text(
            """
        UPDATE jobs.jobs j
        SET location = l.region
        FROM jobs.locations l
        WHERE j.location_id = l.id
    """
        )
    )

    connection.execute(
        sa.text(
            """
        UPDATE jobs.jobs j
        SET extra_data = jsonb_build_object(
            'category', cat.name,
            'industry', ind.name,
            'experience_months', j.experience_months
        )
        FROM jobs.categories cat, jobs.industries ind
        WHERE j.category_id = cat.id AND j.industry_id = ind.id
    """
        )
    )
