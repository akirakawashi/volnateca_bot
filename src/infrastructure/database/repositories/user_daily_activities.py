from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlmodel import col

from application.interface.repositories.user_daily_activities import (
    IUserDailyActivityRepository,
    UserDailyActivityRecord,
)
from infrastructure.database.models.user_daily_activities import UserDailyActivity
from infrastructure.database.repositories.base import SQLAlchemyRepository


class UserDailyActivityRepository(SQLAlchemyRepository, IUserDailyActivityRepository):
    """Репозиторий дневной активности пользователя."""

    async def get_by_user_and_date(
        self,
        *,
        users_id: int,
        activity_date: date,
    ) -> UserDailyActivityRecord | None:
        activity = await self._get_by_user_and_date(
            users_id=users_id,
            activity_date=activity_date,
        )
        return self._to_record(activity=activity) if activity is not None else None

    async def create_if_not_exists(
        self,
        *,
        users_id: int,
        activity_date: date,
        streak_days: int,
    ) -> tuple[UserDailyActivityRecord, bool]:
        try:
            async with self._session.begin_nested():
                activity = UserDailyActivity(
                    users_id=users_id,
                    activity_date=activity_date,
                    streak_days=streak_days,
                )
                self._session.add(activity)
                await self._session.flush()
        except IntegrityError:
            existing = await self._get_by_user_and_date(
                users_id=users_id,
                activity_date=activity_date,
            )
            if existing is None:
                raise
            return self._to_record(activity=existing), False

        return self._to_record(activity=activity), True

    async def _get_by_user_and_date(
        self,
        *,
        users_id: int,
        activity_date: date,
    ) -> UserDailyActivity | None:
        result = await self._session.execute(
            select(UserDailyActivity).where(
                col(UserDailyActivity.users_id) == users_id,
                col(UserDailyActivity.activity_date) == activity_date,
            ),
        )
        return result.scalar_one_or_none()

    @staticmethod
    def _to_record(activity: UserDailyActivity) -> UserDailyActivityRecord:
        return UserDailyActivityRecord(
            users_id=activity.users_id,
            activity_date=activity.activity_date,
            streak_days=activity.streak_days,
        )
