"""Add VK referral intents

Revision ID: 2f41b6a8c9d0
Revises: 7dfe2c29004d
Create Date: 2026-05-27 23:45:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "2f41b6a8c9d0"
down_revision: str | Sequence[str] | None = "7dfe2c29004d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "vk_referral_intents",
        sa.Column("vk_referral_intents_id", sa.Integer(), nullable=False),
        sa.Column("invited_vk_user_id", sa.Integer(), nullable=False),
        sa.Column("raw_ref", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("vk_referral_intents_id", name=op.f("pk_vk_referral_intents")),
        sa.UniqueConstraint(
            "invited_vk_user_id",
            name="uq_vk_referral_intents_invited_vk_user_id",
        ),
    )
    op.create_index(
        op.f("ix_vk_referral_intents_invited_vk_user_id"),
        "vk_referral_intents",
        ["invited_vk_user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_vk_referral_intents_invited_vk_user_id"),
        table_name="vk_referral_intents",
    )
    op.drop_table("vk_referral_intents")
