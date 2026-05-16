"""drop image_url from quiz_questions

Revision ID: 7f1c4a7e6d8b
Revises: c90d60cb6b52
Create Date: 2026-05-16 00:00:00.000000
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7f1c4a7e6d8b"
down_revision: str | None = "c90d60cb6b52"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("quiz_questions", "image_url")


def downgrade() -> None:
    op.add_column(
        "quiz_questions",
        sa.Column("image_url", sa.String(), nullable=True),
    )
