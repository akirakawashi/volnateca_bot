from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlmodel import col

from application.interface.repositories.achievements import AchievementRecord, IAchievementRepository
from infrastructure.database.models.achievements import Achievement
from infrastructure.database.models.user_achievements import UserAchievement
from infrastructure.database.repositories.base import SQLAlchemyRepository


class AchievementRepository(SQLAlchemyRepository, IAchievementRepository):
    """Репозиторий справочника достижений и фактов их выдачи."""

    async def get_by_code(self, code: str) -> AchievementRecord | None:
        result = await self._session.execute(
            select(Achievement).where(col(Achievement.code) == code),
        )
        achievement = result.scalar_one_or_none()
        if achievement is None:
            return None
        return AchievementRecord(
            achievements_id=achievement.achievements_id,  # type: ignore[arg-type]
            code=achievement.code,
            achievement_name=achievement.achievement_name,
            points=achievement.points,
        )

    async def is_awarded(
        self,
        *,
        users_id: int,
        achievements_id: int,
        achievement_key: str,
    ) -> bool:
        result = await self._session.execute(
            select(UserAchievement).where(
                col(UserAchievement.users_id) == users_id,
                col(UserAchievement.achievements_id) == achievements_id,
                col(UserAchievement.achievement_key) == achievement_key,
            ),
        )
        return result.scalar_one_or_none() is not None

    async def count_awarded_keys_by_code(
        self,
        *,
        users_id: int,
        achievement_code: str,
        achievement_keys: tuple[str, ...],
    ) -> int:
        if not achievement_keys:
            return 0

        result = await self._session.execute(
            select(func.count(func.distinct(UserAchievement.achievement_key)))
            .join(
                Achievement,
                col(UserAchievement.achievements_id) == col(Achievement.achievements_id),
            )
            .where(
                col(UserAchievement.users_id) == users_id,
                col(Achievement.code) == achievement_code,
                col(UserAchievement.achievement_key).in_(achievement_keys),
            ),
        )
        return int(result.scalar_one())

    async def award_if_not_exists(
        self,
        *,
        users_id: int,
        achievements_id: int,
        transactions_id: int,
        achievement_key: str,
        points: int,
    ) -> bool:
        try:
            async with self._session.begin_nested():
                user_achievement = UserAchievement(
                    users_id=users_id,
                    achievements_id=achievements_id,
                    transactions_id=transactions_id,
                    achievement_key=achievement_key,
                    points_awarded=points,
                )
                self._session.add(user_achievement)
                await self._session.flush()
        except IntegrityError:
            return False
        return True
