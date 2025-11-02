"""create jobs table

Revision ID: de9ecbbf34c7
Revises: 05690e29e15e
Create Date: 2025-11-02 16:13:08.922292

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision: str = "de9ecbbf34c7"
down_revision: Union[str, None] = "05690e29e15e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create jobs table in the jobs schema
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("company", sa.String(length=300), nullable=False),
        sa.Column("location", sa.String(length=300), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("job_type", sa.String(length=100), nullable=True),
        sa.Column("experience_level", sa.String(length=100), nullable=True),
        sa.Column("salary_min", sa.Float(), nullable=True),
        sa.Column("salary_max", sa.Float(), nullable=True),
        sa.Column("salary_currency", sa.String(length=10), nullable=True, server_default="USD"),
        sa.Column("external_id", sa.String(length=300), nullable=True),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("is_remote", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("extra_data", JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_id"),
        schema="jobs",
    )

    # Create indexes
    op.create_index("ix_jobs_id", "jobs", ["id"], schema="jobs")
    op.create_index("ix_jobs_title", "jobs", ["title"], schema="jobs")
    op.create_index("ix_jobs_company", "jobs", ["company"], schema="jobs")
    op.create_index("ix_jobs_external_id", "jobs", ["external_id"], schema="jobs")
    op.create_index("ix_jobs_source", "jobs", ["source"], schema="jobs")
    op.create_index("ix_jobs_is_active", "jobs", ["is_active"], schema="jobs")
    op.create_index("ix_jobs_is_remote", "jobs", ["is_remote"], schema="jobs")


def downgrade() -> None:
    # Drop the jobs table
    op.drop_table("jobs", schema="jobs")
