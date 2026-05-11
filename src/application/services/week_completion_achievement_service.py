from application.interface.repositories.achievements import IAchievementRepository
from application.interface.repositories.tasks import ITaskRepository
from application.services.award_achievement_service import (
    AchievementAwardSpec,
    AwardAchievementOutcome,
    AwardAchievementOutcomeStatus,
    AwardAchievementService,
)

WEEK_COMPLETION_ACHIEVEMENT_CODE = "week_completion"


class WeekCompletionAchievementService:
    """Проверяет и выдаёт бонус за выполнение всех заданий недели."""

    def __init__(
        self,
        tasks: ITaskRepository,
        achievements: IAchievementRepository,
        award_achievement_service: AwardAchievementService,
    ) -> None:
        self._tasks = tasks
        self._achievements = achievements
        self._award_achievement_service = award_achievement_service

    async def award_if_week_completed(
        self,
        *,
        vk_user_id: int,
        week_number: int | None,
    ) -> AwardAchievementOutcome | None:
        if week_number is None:
            return None

        if not await self._tasks.is_week_completed_by_vk_user(
            vk_user_id=vk_user_id,
            week_number=week_number,
        ):
            return None

        achievement = await self._achievements.get_by_code(code=WEEK_COMPLETION_ACHIEVEMENT_CODE)
        if achievement is None:
            return None

        outcome = await self._award_achievement_service.award(
            vk_user_id=vk_user_id,
            achievement=AchievementAwardSpec(
                achievements_id=achievement.achievements_id,
                achievement_name=achievement.achievement_name,
                points=achievement.points,
            ),
            achievement_key=build_week_completion_key(week_number=week_number),
        )
        return outcome if outcome.status == AwardAchievementOutcomeStatus.COMPLETED else None


def build_week_completion_key(*, week_number: int) -> str:
    return f"week_{week_number:02d}"


__all__ = [
    "WEEK_COMPLETION_ACHIEVEMENT_CODE",
    "WeekCompletionAchievementService",
    "build_week_completion_key",
]
