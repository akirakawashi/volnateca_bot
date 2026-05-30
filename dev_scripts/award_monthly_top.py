"""
TODO DEV: удалить dev_scripts/ перед релизом — только для локальной отладки.

Award monthly_top_10 achievement for a selected month.

Run from the project root:
    poetry run python dev_scripts/award_monthly_top.py --month 2026-07
"""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from application.command.award_monthly_top import AwardMonthlyTopCommand, AwardMonthlyTopHandler
from application.services.award_achievement_service import AwardAchievementService
from infrastructure.database.repositories.achievements import AchievementRepository
from infrastructure.database.repositories.transactions import TransactionRepository
from infrastructure.database.repositories.users import UserRepository
from infrastructure.database.uow import SQLAlchemyBaseUoW
from settings.factory import ConfigFactory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Award monthly_top_10 for selected month.")
    parser.add_argument("--month", required=True, help="Month in YYYY-MM format.")
    parser.add_argument("--limit", type=int, default=10, help="How many users to award. Default: 10.")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    cfg = ConfigFactory()
    engine = create_async_engine(cfg.db.dsn(), echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    try:
        async with async_session() as session:
            user_repository = UserRepository(session=session)
            achievement_repository = AchievementRepository(session=session)
            transaction_repository = TransactionRepository(session=session)
            award_achievement_service = AwardAchievementService(
                users=user_repository,
                achievements=achievement_repository,
                transactions=transaction_repository,
            )
            handler = AwardMonthlyTopHandler(
                transaction_repository=transaction_repository,
                achievement_repository=achievement_repository,
                award_achievement_service=award_achievement_service,
                uow=SQLAlchemyBaseUoW(session=session),
                project_timezone=cfg.app.project_timezone,
            )
            result = await handler(
                command_data=AwardMonthlyTopCommand(
                    month=args.month,
                    limit=args.limit,
                ),
            )

        if not result.achievement_found:
            print("Achievement 'monthly_top_10' not found. Run seed_achievements.py first.")
            return

        print(f"Month: {result.month}")
        print(f"Period UTC: {result.period_start_at.isoformat()} - {result.period_end_at.isoformat()}")
        if not result.awards:
            print("No users with accruals for this month.")
            return

        for award in result.awards:
            print(
                f"#{award.rank}: users_id={award.users_id}, "
                f"vk_user_id={award.vk_user_id}, "
                f"monthly_points={award.monthly_points}, "
                f"status={award.status.value}, "
                f"awarded={award.points_awarded}, "
                f"balance={award.balance_points}",
            )
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
