"""add prize promo codes

Revision ID: f15c9a7d2b81
Revises: 3b64a9157361
Create Date: 2026-06-11 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel  # noqa: F401


revision: str = "f15c9a7d2b81"
down_revision: str | Sequence[str] | None = "3b64a9157361"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


prize_promo_code_status = sa.Enum(
    "available",
    "assigned",
    "void",
    name="prize_promo_code_status",
)


def upgrade() -> None:
    op.create_table(
        "prize_promo_codes",
        sa.Column("prize_promo_codes_id", sa.Integer(), nullable=False),
        sa.Column("prizes_id", sa.Integer(), nullable=False),
        sa.Column("promo_code", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("status", prize_promo_code_status, nullable=False),
        sa.Column("prize_redemptions_id", sa.Integer(), nullable=True),
        sa.Column("assigned_to_users_id", sa.Integer(), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["assigned_to_users_id"], ["users.users_id"], name=op.f("fk_prize_promo_codes_assigned_to_users_id_users")),
        sa.ForeignKeyConstraint(["prize_redemptions_id"], ["prize_redemptions.prize_redemptions_id"], name=op.f("fk_prize_promo_codes_prize_redemptions_id_prize_redemptions")),
        sa.ForeignKeyConstraint(["prizes_id"], ["prizes.prizes_id"], name=op.f("fk_prize_promo_codes_prizes_id_prizes")),
        sa.PrimaryKeyConstraint("prize_promo_codes_id", name=op.f("pk_prize_promo_codes")),
        sa.UniqueConstraint("prize_redemptions_id", name="uq_prize_promo_codes_prize_redemptions_id"),
        sa.UniqueConstraint("prizes_id", "promo_code", name="uq_prize_promo_codes_prizes_id_promo_code"),
    )
    op.create_index(op.f("ix_prize_promo_codes_assigned_to_users_id"), "prize_promo_codes", ["assigned_to_users_id"], unique=False)
    op.create_index(op.f("ix_prize_promo_codes_prizes_id"), "prize_promo_codes", ["prizes_id"], unique=False)
    op.create_index("ix_prize_promo_codes_prizes_id_status", "prize_promo_codes", ["prizes_id", "status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_prize_promo_codes_prizes_id_status", table_name="prize_promo_codes")
    op.drop_index(op.f("ix_prize_promo_codes_prizes_id"), table_name="prize_promo_codes")
    op.drop_index(op.f("ix_prize_promo_codes_assigned_to_users_id"), table_name="prize_promo_codes")
    op.drop_table("prize_promo_codes")
    prize_promo_code_status.drop(op.get_bind(), checkfirst=True)
