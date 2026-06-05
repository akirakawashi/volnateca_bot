"""add_image_attachment_to_tasks

Revision ID: 7d94d7331d64
Revises: 3b64a9157361
Create Date: 2026-06-05 15:14:23.609494
"""

from collections.abc import Sequence

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401
import sqlmodel  # noqa: F401



revision: str = '7d94d7331d64'
down_revision: str | Sequence[str] | None = '3b64a9157361'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('tasks', sa.Column('image_attachment', sqlmodel.sql.sqltypes.AutoString(), nullable=True))


def downgrade() -> None:
    op.drop_column('tasks', 'image_attachment')
