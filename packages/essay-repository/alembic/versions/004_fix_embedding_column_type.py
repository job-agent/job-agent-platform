"""fix embedding column type to use pgvector

Revision ID: 004_fix_embedding_column_type
Revises: 003_add_search_columns
Create Date: 2026-01-07

This migration converts the embedding column from ARRAY(Float) to pgvector's vector type.
This is required for the <=> operator to work properly for vector similarity search.
"""

from typing import Sequence, Union

from alembic import op


revision: str = "004_fix_embedding_column_type"
down_revision: Union[str, None] = "003_add_search_columns"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convert embedding column from double precision[] to vector type
    # The vector extension should already be enabled from the previous migration
    # Using 512 dimensions for sentence-transformers/distiluse-base-multilingual-cased-v2
    op.execute(
        """
        ALTER TABLE essays.essays
        ALTER COLUMN embedding TYPE vector(512) USING embedding::vector(512)
        """
    )


def downgrade() -> None:
    # Convert back from vector to double precision[]
    op.execute(
        """
        ALTER TABLE essays.essays
        ALTER COLUMN embedding TYPE double precision[] USING embedding::double precision[]
        """
    )
