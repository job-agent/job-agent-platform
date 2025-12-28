"""migrate_skills_to_jsonb

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-12-27 12:00:00.000000

Migrates skill columns from ARRAY(String) to JSONB to support 2D skill structure.
The new format uses nested lists where:
- Outer list = AND relationships (all groups required)
- Inner lists = OR relationships (alternatives within a group)

Example: [["JavaScript", "Python"], ["React"]] means
"(JavaScript OR Python) AND React"

Existing flat arrays are converted to the 2D format treating each skill as a solo AND group:
["A", "B", "C"] -> [["A"], ["B"], ["C"]]
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB


revision: str = "b2c3d4e5f6g7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Migrate skills columns from ARRAY(String) to JSONB with 2D structure.

    Steps:
    1. Add new JSONB columns with temporary names
    2. Migrate existing data: transform flat arrays to 2D format
    3. Drop old ARRAY columns
    4. Rename new columns to original names
    """
    # Step 1: Add new JSONB columns with temporary names
    op.add_column(
        "jobs",
        sa.Column("must_have_skills_new", JSONB, nullable=True),
        schema="jobs",
    )
    op.add_column(
        "jobs",
        sa.Column("nice_to_have_skills_new", JSONB, nullable=True),
        schema="jobs",
    )

    # Step 2: Migrate existing data
    # Transform flat array ["A", "B", "C"] to 2D format [["A"], ["B"], ["C"]]
    connection = op.get_bind()

    # For must_have_skills: Convert each element to a single-item array
    connection.execute(
        sa.text(
            """
        UPDATE jobs.jobs
        SET must_have_skills_new = (
            SELECT jsonb_agg(jsonb_build_array(skill))
            FROM unnest(must_have_skills) AS skill
        )
        WHERE must_have_skills IS NOT NULL
          AND array_length(must_have_skills, 1) > 0
    """
        )
    )

    # For nice_to_have_skills: Convert each element to a single-item array
    connection.execute(
        sa.text(
            """
        UPDATE jobs.jobs
        SET nice_to_have_skills_new = (
            SELECT jsonb_agg(jsonb_build_array(skill))
            FROM unnest(nice_to_have_skills) AS skill
        )
        WHERE nice_to_have_skills IS NOT NULL
          AND array_length(nice_to_have_skills, 1) > 0
    """
        )
    )

    # Step 3: Drop old ARRAY columns
    op.drop_column("jobs", "must_have_skills", schema="jobs")
    op.drop_column("jobs", "nice_to_have_skills", schema="jobs")

    # Step 4: Rename new columns to original names
    op.alter_column(
        "jobs",
        "must_have_skills_new",
        new_column_name="must_have_skills",
        schema="jobs",
    )
    op.alter_column(
        "jobs",
        "nice_to_have_skills_new",
        new_column_name="nice_to_have_skills",
        schema="jobs",
    )


def downgrade() -> None:
    """Revert JSONB columns back to ARRAY(String).

    Warning: This loses OR relationship information. All skills within OR groups
    are flattened to individual AND requirements.
    """
    # Step 1: Add old ARRAY columns with temporary names
    op.add_column(
        "jobs",
        sa.Column(
            "must_have_skills_old",
            sa.ARRAY(sa.String()),
            nullable=True,
        ),
        schema="jobs",
    )
    op.add_column(
        "jobs",
        sa.Column(
            "nice_to_have_skills_old",
            sa.ARRAY(sa.String()),
            nullable=True,
        ),
        schema="jobs",
    )

    # Step 2: Migrate data back
    # Flatten 2D structure [["A", "B"], ["C"]] to flat array ["A", "B", "C"]
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
        UPDATE jobs.jobs
        SET must_have_skills_old = (
            SELECT array_agg(skill)
            FROM (
                SELECT jsonb_array_elements_text(jsonb_array_elements(must_have_skills)) AS skill
            ) AS skills
        )
        WHERE must_have_skills IS NOT NULL
          AND jsonb_array_length(must_have_skills) > 0
    """
        )
    )

    connection.execute(
        sa.text(
            """
        UPDATE jobs.jobs
        SET nice_to_have_skills_old = (
            SELECT array_agg(skill)
            FROM (
                SELECT jsonb_array_elements_text(jsonb_array_elements(nice_to_have_skills)) AS skill
            ) AS skills
        )
        WHERE nice_to_have_skills IS NOT NULL
          AND jsonb_array_length(nice_to_have_skills) > 0
    """
        )
    )

    # Step 3: Drop JSONB columns
    op.drop_column("jobs", "must_have_skills", schema="jobs")
    op.drop_column("jobs", "nice_to_have_skills", schema="jobs")

    # Step 4: Rename old columns back to original names
    op.alter_column(
        "jobs",
        "must_have_skills_old",
        new_column_name="must_have_skills",
        schema="jobs",
    )
    op.alter_column(
        "jobs",
        "nice_to_have_skills_old",
        new_column_name="nice_to_have_skills",
        schema="jobs",
    )
