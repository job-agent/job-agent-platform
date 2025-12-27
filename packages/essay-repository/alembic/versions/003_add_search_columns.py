"""add search columns for hybrid search

Revision ID: 003_add_search_columns
Revises: 002_create_essays_table
Create Date: 2025-12-21

This migration adds the infrastructure for hybrid search:
1. Enables pgvector extension for vector similarity search
2. Adds embedding column (ARRAY of Float, 1536 dimensions for OpenAI)
3. Adds search_vector column (TSVECTOR) for full-text search
4. Creates GIN index on search_vector for fast text search
5. Creates trigger to auto-populate search_vector on INSERT/UPDATE
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY


revision: str = "003_add_search_columns"
down_revision: Union[str, None] = "002_create_essays_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension for vector similarity search
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Add embedding column for vector search (1536 dimensions for OpenAI embeddings)
    op.add_column(
        "essays",
        sa.Column("embedding", ARRAY(sa.Float), nullable=True),
        schema="essays",
    )

    # Add search_vector column for full-text search
    op.execute(
        """
        ALTER TABLE essays.essays
        ADD COLUMN search_vector tsvector
        """
    )

    # Create GIN index on search_vector for fast full-text search
    op.execute(
        """
        CREATE INDEX ix_essays_search_vector
        ON essays.essays
        USING GIN (search_vector)
        """
    )

    # Create function to generate search_vector from essay content
    # Weight 'A' for question and keywords (higher importance)
    # Weight 'B' for answer (lower importance)
    op.execute(
        """
        CREATE OR REPLACE FUNCTION essays.update_essay_search_vector()
        RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('english', coalesce(NEW.question, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(NEW.answer, '')), 'B') ||
                setweight(to_tsvector('english', coalesce(array_to_string(NEW.keywords, ' '), '')), 'A');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
        """
    )

    # Create trigger to auto-update search_vector on INSERT or UPDATE
    op.execute(
        """
        CREATE TRIGGER essays_search_vector_update
        BEFORE INSERT OR UPDATE ON essays.essays
        FOR EACH ROW
        EXECUTE FUNCTION essays.update_essay_search_vector()
        """
    )

    # Backfill search_vector for existing rows (if any)
    op.execute(
        """
        UPDATE essays.essays
        SET search_vector =
            setweight(to_tsvector('english', coalesce(question, '')), 'A') ||
            setweight(to_tsvector('english', coalesce(answer, '')), 'B') ||
            setweight(to_tsvector('english', coalesce(array_to_string(keywords, ' '), '')), 'A')
        WHERE search_vector IS NULL
        """
    )


def downgrade() -> None:
    # Drop trigger first
    op.execute("DROP TRIGGER IF EXISTS essays_search_vector_update ON essays.essays")

    # Drop the function
    op.execute("DROP FUNCTION IF EXISTS essays.update_essay_search_vector()")

    # Drop the GIN index
    op.execute("DROP INDEX IF EXISTS essays.ix_essays_search_vector")

    # Drop the search_vector column
    op.drop_column("essays", "search_vector", schema="essays")

    # Drop the embedding column
    op.drop_column("essays", "embedding", schema="essays")

    # Note: We don't drop the pgvector extension as it may be used by other tables
