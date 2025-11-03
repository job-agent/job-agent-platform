"""add_skills_arrays_to_jobs

Revision ID: a361684797bf
Revises: 32bbf7298a3a
Create Date: 2025-11-02 21:43:05.480679

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY


# revision identifiers, used by Alembic.
revision: str = "a361684797bf"
down_revision: Union[str, None] = "32bbf7298a3a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add must_have_skills and nice_to_have_skills array columns to jobs table."""
    op.add_column(
        "jobs", sa.Column("must_have_skills", ARRAY(sa.String()), nullable=True), schema="jobs"
    )
    op.add_column(
        "jobs", sa.Column("nice_to_have_skills", ARRAY(sa.String()), nullable=True), schema="jobs"
    )


def downgrade() -> None:
    """Remove must_have_skills and nice_to_have_skills columns from jobs table."""
    op.drop_column("jobs", "nice_to_have_skills", schema="jobs")
    op.drop_column("jobs", "must_have_skills", schema="jobs")
