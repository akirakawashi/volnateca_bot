"""add task completion evidence

Revision ID: 3f1f2b5c0b9a
Revises: 15b5f59a77d0
Create Date: 2026-05-07 13:20:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = "3f1f2b5c0b9a"
down_revision: str | Sequence[str] | None = "15b5f59a77d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "task_completions",
        sa.Column("evidence_external_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.create_index(
        op.f("ix_task_completions_evidence_external_id"),
        "task_completions",
        ["evidence_external_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_task_completions_evidence_external_id"),
        table_name="task_completions",
    )
    op.drop_column("task_completions", "evidence_external_id")
