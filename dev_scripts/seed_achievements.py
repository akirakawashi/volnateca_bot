"""
TODO DEV: удалить dev_scripts/ перед релизом — только для локальной отладки.

Seed-скрипт: наполняет таблицу achievements начальными данными.

Запуск:
    poetry run python dev_scripts/seed_achievements.py
"""
# ruff: noqa: E402

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from domain.enums.achievement import AchievementRepeatPolicy, AchievementType
from infrastructure.database.models.achievements import Achievement
from settings.factory import ConfigFactory

ACHIEVEMENTS: list[dict] = [
    # --- Реферальные пороги ---
    {
        "code": "referral_milestone_3",
        "achievement_name": "Первые друзья",
        "description": "Пригласи 3 друзей и получи бонус",
        "achievement_type": AchievementType.REFERRAL_MILESTONE,
        "repeat_policy": AchievementRepeatPolicy.ONCE,
        "points": 100,
    },
    {
        "code": "referral_milestone_5",
        "achievement_name": "Команда",
        "description": "Пригласи 5 друзей и получи бонус",
        "achievement_type": AchievementType.REFERRAL_MILESTONE,
        "repeat_policy": AchievementRepeatPolicy.ONCE,
        "points": 200,
    },
    {
        "code": "referral_milestone_10",
        "achievement_name": "Амбассадор",
        "description": "Пригласи 10 друзей и получи бонус",
        "achievement_type": AchievementType.REFERRAL_MILESTONE,
        "repeat_policy": AchievementRepeatPolicy.ONCE,
        "points": 400,
    },
    # --- Недельные и проектные бонусы ---
    {
        "code": "week_completion",
        "achievement_name": "Все задания недели",
        "description": "Выполни все активные задания недели",
        "achievement_type": AchievementType.WEEK_COMPLETION,
        "repeat_policy": AchievementRepeatPolicy.WEEKLY,
        "points": 100,
    },
    {
        "code": "monthly_top_10",
        "achievement_name": "Топ-10 рейтинга месяца",
        "description": "Попади в топ-10 месячного рейтинга участников",
        "achievement_type": AchievementType.MONTHLY_RATING,
        "repeat_policy": AchievementRepeatPolicy.MONTHLY,
        "points": 250,
    },
    {
        "code": "project_completion_12_weeks",
        "achievement_name": "Все 12 недель",
        "description": "Пройди все 12 недель юбилейного проекта",
        "achievement_type": AchievementType.PROJECT_COMPLETION,
        "repeat_policy": AchievementRepeatPolicy.ONCE,
        "points": 500,
    },
]


async def seed(dsn: str) -> None:
    engine = create_async_engine(dsn, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore[call-overload]

    async with async_session() as session:
        for data in ACHIEVEMENTS:
            existing = await session.scalar(
                select(Achievement).where(Achievement.code == data["code"])
            )
            if existing:
                print(f"  [skip]   {data['code']} — уже существует")
                continue
            session.add(Achievement(**data))
            print(f"  [insert] {data['code']} (+{data['points']} ✦)")

        await session.commit()

    await engine.dispose()
    print("Done.")


if __name__ == "__main__":
    cfg = ConfigFactory()
    asyncio.run(seed(cfg.db.dsn()))
