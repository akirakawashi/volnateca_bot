from dataclasses import dataclass

from application.interface.repositories.achievements import IAchievementRepository
from application.services.award_achievement_service import (
    AchievementAwardSpec,
    AwardAchievementOutcomeStatus,
    AwardAchievementService,
)

DAILY_STREAK_ACHIEVEMENTS: dict[int, str] = {
    7: "daily_streak_7",
    30: "daily_streak_30",
}


@dataclass(slots=True, frozen=True, kw_only=True)
class DailyStreakAward:
    streak_days: int
    achievement_name: str
    points_awarded: int
    balance_points: int | None
    level_up: int | None


class DailyStreakAchievementService:
    """Выдаёт достижения за дневные стрики активности."""

    def __init__(
        self,
        achievements: IAchievementRepository,
        award_achievement_service: AwardAchievementService,
    ) -> None:
        self._achievements = achievements
        self._award_achievement_service = award_achievement_service

    async def award_for_streak(
        self,
        *,
        vk_user_id: int,
        streak_days: int,
    ) -> DailyStreakAward | None:
        achievement_code = DAILY_STREAK_ACHIEVEMENTS.get(streak_days)
        if achievement_code is None:
            return None

        achievement = await self._achievements.get_by_code(code=achievement_code)
        if achievement is None:
            return None

        outcome = await self._award_achievement_service.award(
            vk_user_id=vk_user_id,
            achievement=AchievementAwardSpec(
                achievements_id=achievement.achievements_id,
                achievement_name=achievement.achievement_name,
                points=achievement.points,
            ),
            achievement_key="once",
        )
        if outcome.status != AwardAchievementOutcomeStatus.COMPLETED:
            return None

        return DailyStreakAward(
            streak_days=streak_days,
            achievement_name=achievement.achievement_name,
            points_awarded=outcome.points_awarded,
            balance_points=outcome.balance_points,
            level_up=outcome.level_up,
        )


__all__ = [
    "DAILY_STREAK_ACHIEVEMENTS",
    "DailyStreakAchievementService",
    "DailyStreakAward",
]
