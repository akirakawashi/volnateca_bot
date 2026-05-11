from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from application.base_interactor import Interactor
from application.interface.repositories.user_daily_activities import IUserDailyActivityRepository
from application.interface.repositories.users import IUserRepository
from application.interface.uow import IUnitOfWork
from application.services.daily_streak_achievement_service import (
    DailyStreakAchievementService,
    DailyStreakAward,
)

PROJECT_TIMEZONE = ZoneInfo("Europe/Moscow")


@dataclass(slots=True, frozen=True, kw_only=True)
class RecordVKUserActivityCommand:
    vk_user_id: int
    occurred_at: datetime | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class RecordVKUserActivityDTO:
    vk_user_id: int
    users_id: int | None
    activity_recorded: bool
    activity_date: str | None
    streak_days: int | None
    awards: tuple[DailyStreakAward, ...]


class RecordVKUserActivityHandler(
    Interactor[RecordVKUserActivityCommand, RecordVKUserActivityDTO],
):
    """Фиксирует любую пользовательскую активность в VK-боте за текущий день."""

    def __init__(
        self,
        user_repository: IUserRepository,
        daily_activity_repository: IUserDailyActivityRepository,
        daily_streak_achievement_service: DailyStreakAchievementService,
        uow: IUnitOfWork,
        project_timezone: ZoneInfo = PROJECT_TIMEZONE,
    ) -> None:
        self.user_repository = user_repository
        self.daily_activity_repository = daily_activity_repository
        self.daily_streak_achievement_service = daily_streak_achievement_service
        self.uow = uow
        self.project_timezone = project_timezone

    async def __call__(
        self,
        command_data: RecordVKUserActivityCommand,
    ) -> RecordVKUserActivityDTO:
        user = await self.user_repository.get_by_vk_user_id(vk_user_id=command_data.vk_user_id)
        if user is None:
            return self._no_op(vk_user_id=command_data.vk_user_id)

        activity_date = self._get_activity_date(occurred_at=command_data.occurred_at)
        previous_date = activity_date - timedelta(days=1)
        previous_activity = await self.daily_activity_repository.get_by_user_and_date(
            users_id=user.users_id,
            activity_date=previous_date,
        )
        streak_days = 1 if previous_activity is None else previous_activity.streak_days + 1

        activity, created = await self.daily_activity_repository.create_if_not_exists(
            users_id=user.users_id,
            activity_date=activity_date,
            streak_days=streak_days,
        )
        if not created:
            return RecordVKUserActivityDTO(
                vk_user_id=command_data.vk_user_id,
                users_id=user.users_id,
                activity_recorded=False,
                activity_date=activity.activity_date.isoformat(),
                streak_days=activity.streak_days,
                awards=(),
            )

        awards: list[DailyStreakAward] = []
        award = await self.daily_streak_achievement_service.award_for_streak(
            vk_user_id=command_data.vk_user_id,
            streak_days=activity.streak_days,
        )
        if award is not None:
            awards.append(award)

        await self.uow.commit()
        return RecordVKUserActivityDTO(
            vk_user_id=command_data.vk_user_id,
            users_id=user.users_id,
            activity_recorded=True,
            activity_date=activity.activity_date.isoformat(),
            streak_days=activity.streak_days,
            awards=tuple(awards),
        )

    def _get_activity_date(self, *, occurred_at: datetime | None) -> date:
        event_time = occurred_at if occurred_at is not None else datetime.now(tz=UTC)
        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=UTC)
        return event_time.astimezone(self.project_timezone).date()

    @staticmethod
    def _no_op(*, vk_user_id: int) -> RecordVKUserActivityDTO:
        return RecordVKUserActivityDTO(
            vk_user_id=vk_user_id,
            users_id=None,
            activity_recorded=False,
            activity_date=None,
            streak_days=None,
            awards=(),
        )


__all__ = [
    "PROJECT_TIMEZONE",
    "RecordVKUserActivityCommand",
    "RecordVKUserActivityDTO",
    "RecordVKUserActivityHandler",
]
