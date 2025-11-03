"""remove_timestamps_from_normalized_tables

Revision ID: 723f0730a321
Revises: 9313e7f4c4bb
Create Date: 2025-11-02 17:39:18.935913

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "723f0730a321"
down_revision: Union[str, None] = "9313e7f4c4bb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove timestamp columns from normalized tables."""

    # Drop created_at and updated_at from companies table
    op.drop_column("companies", "created_at", schema="jobs")
    op.drop_column("companies", "updated_at", schema="jobs")

    # Drop created_at and updated_at from locations table
    op.drop_column("locations", "created_at", schema="jobs")
    op.drop_column("locations", "updated_at", schema="jobs")

    # Drop created_at and updated_at from categories table
    op.drop_column("categories", "created_at", schema="jobs")
    op.drop_column("categories", "updated_at", schema="jobs")

    # Drop created_at and updated_at from industries table
    op.drop_column("industries", "created_at", schema="jobs")
    op.drop_column("industries", "updated_at", schema="jobs")


def downgrade() -> None:
    """Restore timestamp columns to normalized tables."""

    # Add back created_at and updated_at to companies table
    op.add_column(
        "companies",
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        schema="jobs",
    )
    op.add_column(
        "companies",
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        schema="jobs",
    )

    # Add back created_at and updated_at to locations table
    op.add_column(
        "locations",
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        schema="jobs",
    )
    op.add_column(
        "locations",
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        schema="jobs",
    )

    # Add back created_at and updated_at to categories table
    op.add_column(
        "categories",
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        schema="jobs",
    )
    op.add_column(
        "categories",
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        schema="jobs",
    )

    # Add back created_at and updated_at to industries table
    op.add_column(
        "industries",
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        schema="jobs",
    )
    op.add_column(
        "industries",
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        schema="jobs",
    )
