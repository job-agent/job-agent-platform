"""create jobs schema

Revision ID: 05690e29e15e
Revises:
Create Date: 2025-11-02 16:12:35.969413

"""

from typing import Sequence, Union

from alembic import op


revision: str = "05690e29e15e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.execute("CREATE SCHEMA IF NOT EXISTS jobs")


def downgrade() -> None:

    op.execute("DROP SCHEMA IF EXISTS jobs CASCADE")
