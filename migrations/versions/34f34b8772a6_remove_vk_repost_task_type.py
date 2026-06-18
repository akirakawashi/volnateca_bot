"""remove vk repost task type

Revision ID: 34f34b8772a6
Revises: f15c9a7d2b81
Create Date: 2026-06-18 19:58:59.090522
"""

from collections.abc import Sequence

from alembic import op


revision: str = "34f34b8772a6"
down_revision: str | Sequence[str] | None = "f15c9a7d2b81"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TASK_TYPE = "task_type"
TASK_TYPE_OLD = "task_type_old"

TASK_TYPE_VALUES = (
    "vk_subscribe",
    "vk_like",
    "vk_comment",
    "vk_poll",
    "quiz",
    "custom",
)
TASK_TYPE_VALUES_WITH_REPOST = (
    "vk_subscribe",
    "vk_like",
    "vk_repost",
    "vk_comment",
    "vk_poll",
    "quiz",
    "custom",
)


def upgrade() -> None:
    op.execute(
        """
        UPDATE tasks
        SET task_type = 'custom',
            is_active = false
        WHERE task_type = 'vk_repost'
        """,
    )
    _replace_task_type_enum(TASK_TYPE_VALUES)


def downgrade() -> None:
    _replace_task_type_enum(TASK_TYPE_VALUES_WITH_REPOST)


def _replace_task_type_enum(values: tuple[str, ...]) -> None:
    values_sql = ", ".join(f"'{value}'" for value in values)
    op.execute(f"ALTER TYPE {TASK_TYPE} RENAME TO {TASK_TYPE_OLD}")
    op.execute(f"CREATE TYPE {TASK_TYPE} AS ENUM ({values_sql})")
    op.execute(
        f"""
        ALTER TABLE tasks
        ALTER COLUMN task_type TYPE {TASK_TYPE}
        USING task_type::text::{TASK_TYPE}
        """,
    )
    op.execute(f"DROP TYPE {TASK_TYPE_OLD}")
