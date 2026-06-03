from dataclasses import dataclass

from application.interface.repositories.achievements import IAchievementRepository
from application.services.award_achievement_service import (
    AchievementAwardSpec,
    AwardAchievementOutcomeStatus,
    AwardAchievementService,
)
from domain.project_rules import (
    PROJECT_COMPLETION_ACHIEVEMENT_CODE,
    PROJECT_COMPLETION_REQUIRED_WEEK_COUNT,
    PROJECT_COMPLETION_REQUIRED_WEEK_KEYS,
    WEEK_COMPLETION_ACHIEVEMENT_CODE,
)


@dataclass(slots=True, frozen=True, kw_only=True)
class ProjectCompletionAward:
    achievement_name: str
    points_awarded: int
    balance_points: int | None
    level_up: int | None


class ProjectCompletionAchievementService:
    """Выдаёт финальный бонус за закрытие всех 12 недель проекта."""

    def __init__(
        self,
        achievements: IAchievementRepository,
        award_achievement_service: AwardAchievementService,
    ) -> None:
        self._achievements = achievements
        self._award_achievement_service = award_achievement_service

    async def award_if_completed(
        self,
        *,
        vk_user_id: int,
        users_id: int,
    ) -> ProjectCompletionAward | None:
        completed_week_count = await self._achievements.count_awarded_keys_by_code(
            users_id=users_id,
            achievement_code=WEEK_COMPLETION_ACHIEVEMENT_CODE,
            achievement_keys=PROJECT_COMPLETION_REQUIRED_WEEK_KEYS,
        )
        if completed_week_count < PROJECT_COMPLETION_REQUIRED_WEEK_COUNT:
            return None

        achievement = await self._achievements.get_by_code(code=PROJECT_COMPLETION_ACHIEVEMENT_CODE)
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

        return ProjectCompletionAward(
            achievement_name=achievement.achievement_name,
            points_awarded=outcome.points_awarded,
            balance_points=outcome.balance_points,
            level_up=outcome.level_up,
        )


__all__ = [
    "PROJECT_COMPLETION_ACHIEVEMENT_CODE",
    "PROJECT_COMPLETION_REQUIRED_WEEK_COUNT",
    "PROJECT_COMPLETION_REQUIRED_WEEK_KEYS",
    "ProjectCompletionAchievementService",
    "ProjectCompletionAward",
]
