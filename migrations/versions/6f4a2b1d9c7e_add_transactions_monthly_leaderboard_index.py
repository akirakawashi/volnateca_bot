"""Add transactions monthly leaderboard index

Revision ID: 6f4a2b1d9c7e
Revises: 2d5f8d8c9b6e
Create Date: 2026-05-27 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op


revision: str = "6f4a2b1d9c7e"
down_revision: str | Sequence[str] | None = "2d5f8d8c9b6e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_transactions_transaction_type_created_at_users_id",
        "transactions",
        ["transaction_type", "created_at", "users_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_transactions_transaction_type_created_at_users_id",
        table_name="transactions",
    )
