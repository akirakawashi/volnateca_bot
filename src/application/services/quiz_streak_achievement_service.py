from dataclasses import dataclass

from application.interface.repositories.achievements import IAchievementRepository
from application.interface.repositories.quiz import IQuizRepository
from application.services.award_achievement_service import (
    AchievementAwardSpec,
    AwardAchievementOutcomeStatus,
    AwardAchievementService,
)

QUIZ_STREAK_ACHIEVEMENT_CODE = "quiz_streak_5"
QUIZ_STREAK_TARGET = 5


@dataclass(slots=True, frozen=True, kw_only=True)
class QuizStreakAward:
    streak_count: int
    achievement_name: str
    points_awarded: int
    balance_points: int | None
    level_up: int | None


class QuizStreakAchievementService:
    """Выдаёт достижение за серию завершённых викторин без ошибок."""

    def __init__(
        self,
        quiz_repository: IQuizRepository,
        achievements: IAchievementRepository,
        award_achievement_service: AwardAchievementService,
    ) -> None:
        self._quiz_repository = quiz_repository
        self._achievements = achievements
        self._award_achievement_service = award_achievement_service

    async def award_if_needed(self, *, vk_user_id: int) -> QuizStreakAward | None:
        current_streak = await self._quiz_repository.get_current_correct_quiz_streak(
            vk_user_id=vk_user_id,
        )
        if current_streak < QUIZ_STREAK_TARGET:
            return None

        achievement = await self._achievements.get_by_code(code=QUIZ_STREAK_ACHIEVEMENT_CODE)
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

        return QuizStreakAward(
            streak_count=current_streak,
            achievement_name=achievement.achievement_name,
            points_awarded=outcome.points_awarded,
            balance_points=outcome.balance_points,
            level_up=outcome.level_up,
        )


__all__ = [
    "QUIZ_STREAK_ACHIEVEMENT_CODE",
    "QUIZ_STREAK_TARGET",
    "QuizStreakAchievementService",
    "QuizStreakAward",
]
