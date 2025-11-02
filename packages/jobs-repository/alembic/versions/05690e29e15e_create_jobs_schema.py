"""create jobs schema

Revision ID: 05690e29e15e
Revises: 
Create Date: 2025-11-02 16:12:35.969413

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05690e29e15e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the jobs schema
    op.execute("CREATE SCHEMA IF NOT EXISTS jobs")


def downgrade() -> None:
    # Drop the jobs schema (cascade to drop all objects in it)
    op.execute("DROP SCHEMA IF EXISTS jobs CASCADE")
