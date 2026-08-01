"""initial sqlite schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-01 00:00:00.000000

Schema SQLite completo: sources, jobs (com UNIQUE(source_url) + 9 colunas
extras V1), job_clicks, users, tracked_jobs. Recriado do zero apos troca
PostgreSQL -> SQLite (ver task.md commit 1).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import Enum as SQLEnum

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("base_url", sa.String(length=255), nullable=False),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            SQLEnum("ACTIVE", "INACTIVE", "ERROR", name="sourcestatus"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column(
            "modality",
            SQLEnum("REMOTE", "HYBRID", "ONSITE", name="jobmodality"),
            nullable=False,
        ),
        sa.Column(
            "area",
            SQLEnum(
                "TI_SOFTWARE", "DADOS", "DESIGN", "MARKETING", "NEGOCIOS", "RH",
                "FINANCAS", "ENGENHARIA_OUTRAS", "DIREITO", "PROGRAMA_ESTAGIO",
                "OUTROS",
                name="jobarea",
            ),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("salary", sa.String(length=255), nullable=True),
        sa.Column("company_logo", sa.String(length=1000), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=False),
        sa.Column("source_id", sa.String(length=255), nullable=False),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scraped_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_featured", sa.Boolean(), nullable=False),
        sa.Column(
            "status",
            SQLEnum("ACTIVE", "CLOSED", name="jobstatus"),
            nullable=False,
        ),
        sa.Column("benefits", sa.Text(), nullable=True),
        sa.Column("requirements", sa.Text(), nullable=True),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_pcd", sa.Boolean(), nullable=False),
        sa.Column("contract_type", sa.String(length=50), nullable=True),
        sa.Column("duration_months", sa.Integer(), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("salary_min_cents", sa.Integer(), nullable=True),
        sa.Column("salary_max_cents", sa.Integer(), nullable=True),
        sa.Column("source_uuid", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["source_uuid"], ["sources.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_url", name="uq_jobs_source_url"),
    )

    op.create_table(
        "job_clicks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("clicked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("referrer", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("plan", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "tracked_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=True),
        sa.Column("external_url", sa.String(length=1000), nullable=True),
        sa.Column("external_title", sa.String(length=255), nullable=True),
        sa.Column("external_company", sa.String(length=255), nullable=True),
        sa.Column("external_logo", sa.String(length=1000), nullable=True),
        sa.Column(
            "status",
            SQLEnum(
                "SAVED", "APPLIED", "INTERVIEW", "OFFER", "HIRED", "REJECTED",
                name="trackingstatus",
            ),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("tracked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tracked_jobs_user_id", "tracked_jobs", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_tracked_jobs_user_id", table_name="tracked_jobs")
    op.drop_table("tracked_jobs")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_table("job_clicks")
    op.drop_table("jobs")
    op.drop_table("sources")
