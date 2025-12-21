"""create essays table

Revision ID: 002_create_essays_table
Revises: 001_create_essays_schema
Create Date: 2025-12-21

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, VARCHAR


revision: str = "002_create_essays_table"
down_revision: Union[str, None] = "001_create_essays_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "essays",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("question", sa.Text(), nullable=True),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("keywords", ARRAY(VARCHAR), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        schema="essays",
    )

    op.create_index("ix_essays_id", "essays", ["id"], schema="essays")


def downgrade() -> None:

    op.drop_table("essays", schema="essays")
