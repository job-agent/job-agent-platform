"""normalize_database_structure

Revision ID: 5d2bab6f2e10
Revises: de9ecbbf34c7
Create Date: 2025-11-02 16:37:50.018326

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5d2bab6f2e10"
down_revision: Union[str, None] = "de9ecbbf34c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create normalized tables and migrate existing data."""

    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        schema="jobs",
    )
    op.create_index(op.f("ix_jobs_companies_id"), "companies", ["id"], unique=False, schema="jobs")
    op.create_index(
        op.f("ix_jobs_companies_name"), "companies", ["name"], unique=True, schema="jobs"
    )

    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("region", sa.String(length=300), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("region"),
        schema="jobs",
    )
    op.create_index(op.f("ix_jobs_locations_id"), "locations", ["id"], unique=False, schema="jobs")
    op.create_index(
        op.f("ix_jobs_locations_region"), "locations", ["region"], unique=True, schema="jobs"
    )

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        schema="jobs",
    )
    op.create_index(
        op.f("ix_jobs_categories_id"), "categories", ["id"], unique=False, schema="jobs"
    )
    op.create_index(
        op.f("ix_jobs_categories_name"), "categories", ["name"], unique=True, schema="jobs"
    )

    op.create_table(
        "industries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        schema="jobs",
    )
    op.create_index(
        op.f("ix_jobs_industries_id"), "industries", ["id"], unique=False, schema="jobs"
    )
    op.create_index(
        op.f("ix_jobs_industries_name"), "industries", ["name"], unique=True, schema="jobs"
    )

    op.add_column("jobs", sa.Column("company_id", sa.Integer(), nullable=True), schema="jobs")
    op.add_column("jobs", sa.Column("location_id", sa.Integer(), nullable=True), schema="jobs")
    op.add_column("jobs", sa.Column("category_id", sa.Integer(), nullable=True), schema="jobs")
    op.add_column("jobs", sa.Column("industry_id", sa.Integer(), nullable=True), schema="jobs")
    op.add_column(
        "jobs", sa.Column("experience_months", sa.Integer(), nullable=True), schema="jobs"
    )

    op.create_foreign_key(
        "fk_jobs_company_id",
        "jobs",
        "companies",
        ["company_id"],
        ["id"],
        source_schema="jobs",
        referent_schema="jobs",
    )
    op.create_foreign_key(
        "fk_jobs_location_id",
        "jobs",
        "locations",
        ["location_id"],
        ["id"],
        source_schema="jobs",
        referent_schema="jobs",
    )
    op.create_foreign_key(
        "fk_jobs_category_id",
        "jobs",
        "categories",
        ["category_id"],
        ["id"],
        source_schema="jobs",
        referent_schema="jobs",
    )
    op.create_foreign_key(
        "fk_jobs_industry_id",
        "jobs",
        "industries",
        ["industry_id"],
        ["id"],
        source_schema="jobs",
        referent_schema="jobs",
    )

    op.create_index(
        op.f("ix_jobs_jobs_company_id"), "jobs", ["company_id"], unique=False, schema="jobs"
    )
    op.create_index(
        op.f("ix_jobs_jobs_location_id"), "jobs", ["location_id"], unique=False, schema="jobs"
    )
    op.create_index(
        op.f("ix_jobs_jobs_category_id"), "jobs", ["category_id"], unique=False, schema="jobs"
    )
    op.create_index(
        op.f("ix_jobs_jobs_industry_id"), "jobs", ["industry_id"], unique=False, schema="jobs"
    )

    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
        INSERT INTO jobs.companies (name, created_at, updated_at)
        SELECT DISTINCT company, NOW(), NOW()
        FROM jobs.jobs
        WHERE company IS NOT NULL AND company != ''
        ON CONFLICT (name) DO NOTHING
    """
        )
    )

    connection.execute(
        sa.text(
            """
        INSERT INTO jobs.locations (region, created_at, updated_at)
        SELECT DISTINCT location, NOW(), NOW()
        FROM jobs.jobs
        WHERE location IS NOT NULL AND location != ''
        ON CONFLICT (region) DO NOTHING
    """
        )
    )

    connection.execute(
        sa.text(
            """
        INSERT INTO jobs.categories (name, created_at, updated_at)
        SELECT DISTINCT extra_data->>'category', NOW(), NOW()
        FROM jobs.jobs
        WHERE extra_data->>'category' IS NOT NULL AND extra_data->>'category' != ''
        ON CONFLICT (name) DO NOTHING
    """
        )
    )

    connection.execute(
        sa.text(
            """
        INSERT INTO jobs.industries (name, created_at, updated_at)
        SELECT DISTINCT extra_data->>'industry', NOW(), NOW()
        FROM jobs.jobs
        WHERE extra_data->>'industry' IS NOT NULL AND extra_data->>'industry' != ''
        ON CONFLICT (name) DO NOTHING
    """
        )
    )

    connection.execute(
        sa.text(
            """
        UPDATE jobs.jobs j
        SET company_id = c.id
        FROM jobs.companies c
        WHERE j.company = c.name
    """
        )
    )

    connection.execute(
        sa.text(
            """
        UPDATE jobs.jobs j
        SET location_id = l.id
        FROM jobs.locations l
        WHERE j.location = l.region
    """
        )
    )

    connection.execute(
        sa.text(
            """
        UPDATE jobs.jobs j
        SET category_id = c.id
        FROM jobs.categories c
        WHERE j.extra_data->>'category' = c.name
    """
        )
    )

    connection.execute(
        sa.text(
            """
        UPDATE jobs.jobs j
        SET industry_id = i.id
        FROM jobs.industries i
        WHERE j.extra_data->>'industry' = i.name
    """
        )
    )

    connection.execute(
        sa.text(
            """
        UPDATE jobs.jobs
        SET experience_months = CAST(CAST(extra_data->>'experience_months' AS FLOAT) AS INTEGER)
        WHERE extra_data->>'experience_months' IS NOT NULL
    """
        )
    )

    op.alter_column("jobs", "company", nullable=True, schema="jobs")


def downgrade() -> None:
    """Revert database normalization."""

    op.drop_index(op.f("ix_jobs_jobs_industry_id"), table_name="jobs", schema="jobs")
    op.drop_index(op.f("ix_jobs_jobs_category_id"), table_name="jobs", schema="jobs")
    op.drop_index(op.f("ix_jobs_jobs_location_id"), table_name="jobs", schema="jobs")
    op.drop_index(op.f("ix_jobs_jobs_company_id"), table_name="jobs", schema="jobs")

    op.drop_constraint("fk_jobs_industry_id", "jobs", type_="foreignkey", schema="jobs")
    op.drop_constraint("fk_jobs_category_id", "jobs", type_="foreignkey", schema="jobs")
    op.drop_constraint("fk_jobs_location_id", "jobs", type_="foreignkey", schema="jobs")
    op.drop_constraint("fk_jobs_company_id", "jobs", type_="foreignkey", schema="jobs")

    op.drop_column("jobs", "experience_months", schema="jobs")
    op.drop_column("jobs", "industry_id", schema="jobs")
    op.drop_column("jobs", "category_id", schema="jobs")
    op.drop_column("jobs", "location_id", schema="jobs")
    op.drop_column("jobs", "company_id", schema="jobs")

    op.drop_index(op.f("ix_jobs_industries_name"), table_name="industries", schema="jobs")
    op.drop_index(op.f("ix_jobs_industries_id"), table_name="industries", schema="jobs")
    op.drop_table("industries", schema="jobs")

    op.drop_index(op.f("ix_jobs_categories_name"), table_name="categories", schema="jobs")
    op.drop_index(op.f("ix_jobs_categories_id"), table_name="categories", schema="jobs")
    op.drop_table("categories", schema="jobs")

    op.drop_index(op.f("ix_jobs_locations_region"), table_name="locations", schema="jobs")
    op.drop_index(op.f("ix_jobs_locations_id"), table_name="locations", schema="jobs")
    op.drop_table("locations", schema="jobs")

    op.drop_index(op.f("ix_jobs_companies_name"), table_name="companies", schema="jobs")
    op.drop_index(op.f("ix_jobs_companies_id"), table_name="companies", schema="jobs")
    op.drop_table("companies", schema="jobs")

    op.alter_column("jobs", "company", nullable=False, schema="jobs")
