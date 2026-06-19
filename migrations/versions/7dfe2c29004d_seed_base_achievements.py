"""Seed base achievements

Revision ID: 7dfe2c29004d
Revises: 8962228ee7ba
Create Date: 2026-05-27 07:26:34.514719
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "7dfe2c29004d"
down_revision: str | Sequence[str] | None = "8962228ee7ba"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_ACHIEVEMENTS: tuple[dict[str, object], ...] = (
    {
        "code": "referral_milestone_3",
        "achievement_name": "Первые друзья",
        "description": "Пригласи 3 друзей и получи бонус",
        "achievement_type": "referral_milestone",
        "repeat_policy": "once",
        "points": 100,
        "is_active": True,
    },
    {
        "code": "referral_milestone_5",
        "achievement_name": "Команда",
        "description": "Пригласи 5 друзей и получи бонус",
        "achievement_type": "referral_milestone",
        "repeat_policy": "once",
        "points": 200,
        "is_active": True,
    },
    {
        "code": "referral_milestone_10",
        "achievement_name": "Амбассадор",
        "description": "Пригласи 10 друзей и получи бонус",
        "achievement_type": "referral_milestone",
        "repeat_policy": "once",
        "points": 400,
        "is_active": True,
    },
    {
        "code": "week_completion",
        "achievement_name": "Все задания недели",
        "description": "Выполни все активные задания недели",
        "achievement_type": "week_completion",
        "repeat_policy": "weekly",
        "points": 100,
        "is_active": True,
    },
    {
        "code": "monthly_top_10",
        "achievement_name": "Топ-10 рейтинга месяца",
        "description": "Попади в топ-10 месячного рейтинга участников",
        "achievement_type": "monthly_rating",
        "repeat_policy": "monthly",
        "points": 250,
        "is_active": True,
    },
    {
        "code": "project_completion_12_weeks",
        "achievement_name": "Все 12 недель",
        "description": "Пройди все 12 недель юбилейного проекта",
        "achievement_type": "project_completion",
        "repeat_policy": "once",
        "points": 500,
        "is_active": True,
    },
)

_INSERT_ACHIEVEMENT_SQL = sa.text(
    """
    INSERT INTO achievements (
        code,
        achievement_name,
        description,
        achievement_type,
        repeat_policy,
        points,
        is_active
    ) VALUES (
        :code,
        :achievement_name,
        :description,
        :achievement_type,
        :repeat_policy,
        :points,
        :is_active
    )
    ON CONFLICT (code) DO NOTHING
    """
)


def upgrade() -> None:
    bind = op.get_bind()
    for achievement in _ACHIEVEMENTS:
        bind.execute(_INSERT_ACHIEVEMENT_SQL, achievement)


def downgrade() -> None:
    achievement_table = sa.table("achievements", sa.column("code", sa.String()))
    op.execute(
        sa.delete(achievement_table).where(
            achievement_table.c.code.in_([achievement["code"] for achievement in _ACHIEVEMENTS]),
        ),
    )
