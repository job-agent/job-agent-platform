"""create essays schema

Revision ID: 001_create_essays_schema
Revises:
Create Date: 2025-12-21

"""

from typing import Sequence, Union

from alembic import op


revision: str = "001_create_essays_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.execute("CREATE SCHEMA IF NOT EXISTS essays")


def downgrade() -> None:

    op.execute("DROP SCHEMA IF EXISTS essays CASCADE")
