from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import Date, cast, func, select
from sqlmodel import col

from application.admin.interface.repositories.stats import IStatsAdminRepository
from domain.enums.transaction import TransactionType
from infrastructure.database.models.transactions import Transaction
from infrastructure.database.models.users import User
from infrastructure.database.repositories.base import SQLAlchemyRepository


class StatsAdminRepository(SQLAlchemyRepository, IStatsAdminRepository):
    async def count_daily_active_users_by_accrual(
        self,
        *,
        from_date: date,
        to_date: date,
        project_timezone: ZoneInfo,
    ) -> dict[date, int]:
        tz_name = str(project_timezone)
        range_start = datetime.combine(from_date, time.min, tzinfo=project_timezone)
        range_end = datetime.combine(to_date + timedelta(days=1), time.min, tzinfo=project_timezone)

        local_created_at = func.timezone(tz_name, col(Transaction.created_at))
        day_column = cast(local_created_at, Date).label("day")

        result = await self._session.execute(
            select(
                day_column,
                func.count(func.distinct(col(Transaction.users_id))).label("active_users"),
            )
            .where(
                col(Transaction.transaction_type) == TransactionType.ACCRUAL,
                col(Transaction.created_at) >= range_start,
                col(Transaction.created_at) < range_end,
            )
            .group_by(day_column)
            .order_by(day_column),
        )

        values_by_day: dict[date, int] = {}
        for row in result.all():
            if row.day is None:
                continue
            values_by_day[row.day] = int(row.active_users)
        return values_by_day

    async def count_daily_new_users(
        self,
        *,
        from_date: date,
        to_date: date,
        project_timezone: ZoneInfo,
    ) -> dict[date, int]:
        tz_name = str(project_timezone)
        range_start = datetime.combine(from_date, time.min, tzinfo=project_timezone)
        range_end = datetime.combine(to_date + timedelta(days=1), time.min, tzinfo=project_timezone)

        local_created_at = func.timezone(tz_name, col(User.created_at))
        day_column = cast(local_created_at, Date).label("day")

        result = await self._session.execute(
            select(
                day_column,
                func.count().label("new_users"),
            )
            .where(
                col(User.created_at) >= range_start,
                col(User.created_at) < range_end,
            )
            .group_by(day_column)
            .order_by(day_column),
        )

        values_by_day: dict[date, int] = {}
        for row in result.all():
            if row.day is None:
                continue
            values_by_day[row.day] = int(row.new_users)
        return values_by_day

    async def sum_daily_accrual_points(
        self,
        *,
        from_date: date,
        to_date: date,
        project_timezone: ZoneInfo,
    ) -> dict[date, int]:
        tz_name = str(project_timezone)
        range_start = datetime.combine(from_date, time.min, tzinfo=project_timezone)
        range_end = datetime.combine(to_date + timedelta(days=1), time.min, tzinfo=project_timezone)

        local_created_at = func.timezone(tz_name, col(Transaction.created_at))
        day_column = cast(local_created_at, Date).label("day")

        result = await self._session.execute(
            select(
                day_column,
                func.coalesce(func.sum(col(Transaction.amount)), 0).label("accrual_points"),
            )
            .where(
                col(Transaction.transaction_type) == TransactionType.ACCRUAL,
                col(Transaction.created_at) >= range_start,
                col(Transaction.created_at) < range_end,
            )
            .group_by(day_column)
            .order_by(day_column),
        )

        values_by_day: dict[date, int] = {}
        for row in result.all():
            if row.day is None:
                continue
            values_by_day[row.day] = int(row.accrual_points)
        return values_by_day


__all__ = ["StatsAdminRepository"]
