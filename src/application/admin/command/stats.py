from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from domain.enums.transaction import TransactionSource

from application.admin.dto.stats import (
    AccrualSourceSegmentDTO,
    AccrualSourcesStatsDTO,
    DailyAccrualPointsStatsDTO,
    DailyActivityStatsDTO,
    DailyNewUsersStatsDTO,
)
from application.admin.admin_rules import ADMIN_DAILY_STATS_MAX_RANGE_DAYS
from application.admin.interface.repositories.stats import IStatsAdminRepository
from application.admin.services.daily_activity_stats import (
    build_daily_activity_stats_dto,
    build_daily_stat_points,
    resolve_daily_stats_date_range,
)
from application.base_interactor import Interactor


@dataclass(slots=True, frozen=True, kw_only=True)
class DailyStatsRangeCommand:
    from_date: date | None = None
    to_date: date | None = None
    days: int | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class GetDailyActivityStatsCommand(DailyStatsRangeCommand):
    pass


@dataclass(slots=True, frozen=True, kw_only=True)
class GetDailyNewUsersStatsCommand(DailyStatsRangeCommand):
    pass


@dataclass(slots=True, frozen=True, kw_only=True)
class GetDailyAccrualPointsStatsCommand(DailyStatsRangeCommand):
    pass


@dataclass(slots=True, frozen=True, kw_only=True)
class GetAccrualSourcesStatsCommand(DailyStatsRangeCommand):
    pass


def _resolve_stats_date_range(
    command_data: DailyStatsRangeCommand,
    *,
    project_timezone: ZoneInfo,
) -> tuple[date, date]:
    if command_data.days is not None:
        capped_days = max(1, min(command_data.days, ADMIN_DAILY_STATS_MAX_RANGE_DAYS))
        today = datetime.now(tz=project_timezone).date()
        from_date = today - timedelta(days=capped_days - 1)
        to_date = today
        return from_date, to_date

    return resolve_daily_stats_date_range(
        from_date=command_data.from_date,
        to_date=command_data.to_date,
        project_timezone=project_timezone,
    )


class GetDailyActivityStatsHandler(
    Interactor[GetDailyActivityStatsCommand, DailyActivityStatsDTO],
):
    def __init__(
        self,
        stats_repository: IStatsAdminRepository,
        project_timezone: ZoneInfo,
    ) -> None:
        self._stats = stats_repository
        self._project_timezone = project_timezone

    async def __call__(self, command_data: GetDailyActivityStatsCommand) -> DailyActivityStatsDTO:
        from_date, to_date = _resolve_stats_date_range(
            command_data,
            project_timezone=self._project_timezone,
        )
        values_by_day = await self._stats.count_daily_active_users_by_accrual(
            from_date=from_date,
            to_date=to_date,
            project_timezone=self._project_timezone,
        )
        return build_daily_activity_stats_dto(
            timezone=self._project_timezone,
            from_date=from_date,
            to_date=to_date,
            values_by_day=values_by_day,
        )


class GetDailyNewUsersStatsHandler(
    Interactor[GetDailyNewUsersStatsCommand, DailyNewUsersStatsDTO],
):
    def __init__(
        self,
        stats_repository: IStatsAdminRepository,
        project_timezone: ZoneInfo,
    ) -> None:
        self._stats = stats_repository
        self._project_timezone = project_timezone

    async def __call__(self, command_data: GetDailyNewUsersStatsCommand) -> DailyNewUsersStatsDTO:
        from_date, to_date = _resolve_stats_date_range(
            command_data,
            project_timezone=self._project_timezone,
        )
        values_by_day = await self._stats.count_daily_new_users(
            from_date=from_date,
            to_date=to_date,
            project_timezone=self._project_timezone,
        )
        return DailyNewUsersStatsDTO(
            timezone=str(self._project_timezone),
            from_date=from_date,
            to_date=to_date,
            points=build_daily_stat_points(
                from_date=from_date,
                to_date=to_date,
                values_by_day=values_by_day,
            ),
        )


class GetDailyAccrualPointsStatsHandler(
    Interactor[GetDailyAccrualPointsStatsCommand, DailyAccrualPointsStatsDTO],
):
    def __init__(
        self,
        stats_repository: IStatsAdminRepository,
        project_timezone: ZoneInfo,
    ) -> None:
        self._stats = stats_repository
        self._project_timezone = project_timezone

    async def __call__(
        self,
        command_data: GetDailyAccrualPointsStatsCommand,
    ) -> DailyAccrualPointsStatsDTO:
        from_date, to_date = _resolve_stats_date_range(
            command_data,
            project_timezone=self._project_timezone,
        )
        values_by_day = await self._stats.sum_daily_accrual_points(
            from_date=from_date,
            to_date=to_date,
            project_timezone=self._project_timezone,
        )
        return DailyAccrualPointsStatsDTO(
            timezone=str(self._project_timezone),
            from_date=from_date,
            to_date=to_date,
            points=build_daily_stat_points(
                from_date=from_date,
                to_date=to_date,
                values_by_day=values_by_day,
            ),
        )


class GetAccrualSourcesStatsHandler(
    Interactor[GetAccrualSourcesStatsCommand, AccrualSourcesStatsDTO],
):
    def __init__(
        self,
        stats_repository: IStatsAdminRepository,
        project_timezone: ZoneInfo,
    ) -> None:
        self._stats = stats_repository
        self._project_timezone = project_timezone

    async def __call__(
        self,
        command_data: GetAccrualSourcesStatsCommand,
    ) -> AccrualSourcesStatsDTO:
        from_date, to_date = _resolve_stats_date_range(
            command_data,
            project_timezone=self._project_timezone,
        )
        values_by_source = await self._stats.sum_accrual_points_by_source(
            from_date=from_date,
            to_date=to_date,
            project_timezone=self._project_timezone,
        )
        segments = tuple(
            AccrualSourceSegmentDTO(
                source=source.value,
                value=values_by_source.get(source, 0),
            )
            for source in TransactionSource
            if values_by_source.get(source, 0) > 0
        )
        segments = tuple(sorted(segments, key=lambda segment: segment.value, reverse=True))
        total = sum(segment.value for segment in segments)
        return AccrualSourcesStatsDTO(
            timezone=str(self._project_timezone),
            from_date=from_date,
            to_date=to_date,
            total=total,
            segments=segments,
        )


__all__ = [
    "DailyStatsRangeCommand",
    "GetAccrualSourcesStatsCommand",
    "GetAccrualSourcesStatsHandler",
    "GetDailyAccrualPointsStatsCommand",
    "GetDailyAccrualPointsStatsHandler",
    "GetDailyActivityStatsCommand",
    "GetDailyActivityStatsHandler",
    "GetDailyNewUsersStatsCommand",
    "GetDailyNewUsersStatsHandler",
]
