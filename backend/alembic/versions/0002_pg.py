"""postgresql schema with full-text search

Revision ID: 0002_pg
Revises: 0001_initial
Create Date: 2026-08-01 12:00:00.000000

Migrates the schema for PostgreSQL: drops SQLite FTS5 triggers/virtual
table and adds pg_trgm (gin_trgm_ops) indexes plus a materialised tsvector
column with a GIN index for full-text search.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import Enum as SQLEnum

revision: str = "0002_pg"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _uuid4():
    import uuid

    return str(uuid.uuid4())


def upgrade() -> None:
    # ---------------------------------------------------------------
    # Enable extensions
    # ---------------------------------------------------------------
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")

    # ---------------------------------------------------------------
    # Drop SQLite-specific FTS5 objects (only if they exist)
    # ---------------------------------------------------------------
    # In a fresh PG, these won't exist; ignore errors.
    op.execute("DROP TRIGGER IF EXISTS jobs_fts_update ON jobs;")
    op.execute("DROP TRIGGER IF EXISTS jobs_fts_delete ON jobs;")
    op.execute("DROP TRIGGER IF EXISTS jobs_fts_insert ON jobs;")
    op.execute("DROP TABLE IF EXISTS jobs_fts;")

    # ---------------------------------------------------------------
    # Add pg_trgm indexes for ilike / pattern-matching performance
    # ---------------------------------------------------------------
    op.create_index(
        "ix_jobs_title_trgm",
        "jobs",
        ["title"],
        postgresql_using="gin",
        postgresql_ops={"title": "gin_trgm_ops"},
    )
    op.create_index(
        "ix_jobs_company_trgm",
        "jobs",
        ["company"],
        postgresql_using="gin",
        postgresql_ops={"company": "gin_trgm_ops"},
    )
    op.create_index(
        "ix_jobs_location_trgm",
        "jobs",
        ["location"],
        postgresql_using="gin",
        postgresql_ops={"location": "gin_trgm_ops"},
    )

    """postgresql schema with full-text search

Revision ID: 0002_pg
Revises: 0001_initial
Create Date: 2026-08-01 12:00:00.000000

Adiciona pg_trgm indexes para performance de LIKE/ILIKE e
tsvector + GIN index + trigger para full-text search em portugues.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_pg"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")

    # --------------- pg_trgm indexes for ilike performance ---------------
    op.create_index(
        "ix_jobs_title_trgm",
        "jobs",
        ["title"],
        postgresql_using="gin",
        postgresql_ops={"title": "gin_trgm_ops"},
    )
    op.create_index(
        "ix_jobs_company_trgm",
        "jobs",
        ["company"],
        postgresql_using="gin",
        postgresql_ops={"company": "gin_trgm_ops"},
    )
    op.create_index(
        "ix_jobs_location_trgm",
        "jobs",
        ["location"],
        postgresql_using="gin",
        postgresql_ops={"location": "gin_trgm_ops"},
    )

    # --------------- tsvector full-text search ---------------
    op.add_column(
        "jobs",
        sa.Column("search_vector", sa.dialects.postgresql.TSVECTOR(), nullable=True),
    )

    op.execute("""
        CREATE FUNCTION jobs_ftsvector_update() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('portuguese', coalesce(unaccent(NEW.title), '')), 'A') ||
                setweight(to_tsvector('portuguese', coalesce(unaccent(NEW.company), '')), 'B') ||
                setweight(to_tsvector('portuguese', coalesce(unaccent(NEW.description), '')), 'C') ||
                setweight(to_tsvector('portuguese', coalesce(unaccent(NEW.location), '')), 'D');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER tgr_jobs_ftsvector
            BEFORE INSERT OR UPDATE ON "jobs"
            FOR EACH ROW EXECUTE FUNCTION jobs_ftsvector_update();
    """)

    op.create_index(
        "idx_jobs_ftsvector",
        "jobs",
        ["search_vector"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index("idx_jobs_ftsvector", table_name="jobs", postgresql_using="gin")
    op.execute("DROP TRIGGER IF EXISTS tgr_jobs_ftsvector ON jobs;")
    op.execute("DROP FUNCTION IF EXISTS jobs_ftsvector_update;")
    op.drop_column("jobs", "search_vector")

    op.drop_index("idx_jobs_location_trgm", table_name="jobs", postgresql_using="gin")
    op.drop_index("idx_jobs_company_trgm", table_name="jobs", postgresql_using="gin")
    op.drop_index("idx_jobs_title_trgm", table_name="jobs", postgresql_using="gin")