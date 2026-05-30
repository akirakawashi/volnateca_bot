from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from application.admin.dto.stats import DailyActivityStatsDTO, DailyStatPointDTO

DEFAULT_DAILY_STATS_RANGE_DAYS = 30
MAX_DAILY_STATS_RANGE_DAYS = 90

# Backward-compatible aliases for activity stats.
DEFAULT_ACTIVITY_RANGE_DAYS = DEFAULT_DAILY_STATS_RANGE_DAYS
MAX_ACTIVITY_RANGE_DAYS = MAX_DAILY_STATS_RANGE_DAYS


def resolve_daily_stats_date_range(
    *,
    from_date: date | None,
    to_date: date | None,
    project_timezone: ZoneInfo,
    default_days: int = DEFAULT_DAILY_STATS_RANGE_DAYS,
    max_days: int = MAX_DAILY_STATS_RANGE_DAYS,
) -> tuple[date, date]:
    today = datetime.now(tz=project_timezone).date()

    resolved_to = to_date if to_date is not None else today
    resolved_from = (
        from_date if from_date is not None else resolved_to - timedelta(days=default_days - 1)
    )

    if resolved_from > resolved_to:
        msg = "from must be less than or equal to to"
        raise ValueError(msg)

    if (resolved_to - resolved_from).days + 1 > max_days:
        msg = f"date range must not exceed {max_days} days"
        raise ValueError(msg)

    return resolved_from, resolved_to


def resolve_activity_date_range(
    *,
    from_date: date | None,
    to_date: date | None,
    project_timezone: ZoneInfo,
) -> tuple[date, date]:
    return resolve_daily_stats_date_range(
        from_date=from_date,
        to_date=to_date,
        project_timezone=project_timezone,
    )


def build_daily_stat_points(
    *,
    from_date: date,
    to_date: date,
    values_by_day: dict[date, int],
) -> tuple[DailyStatPointDTO, ...]:
    points: list[DailyStatPointDTO] = []
    current = from_date
    while current <= to_date:
        points.append(DailyStatPointDTO(day=current, value=values_by_day.get(current, 0)))
        current += timedelta(days=1)
    return tuple(points)


def build_daily_activity_points(
    *,
    from_date: date,
    to_date: date,
    values_by_day: dict[date, int],
) -> tuple[DailyStatPointDTO, ...]:
    return build_daily_stat_points(
        from_date=from_date,
        to_date=to_date,
        values_by_day=values_by_day,
    )


def build_daily_activity_stats_dto(
    *,
    timezone: ZoneInfo,
    from_date: date,
    to_date: date,
    values_by_day: dict[date, int],
) -> DailyActivityStatsDTO:
    return DailyActivityStatsDTO(
        timezone=str(timezone),
        from_date=from_date,
        to_date=to_date,
        points=build_daily_stat_points(
            from_date=from_date,
            to_date=to_date,
            values_by_day=values_by_day,
        ),
    )


__all__ = [
    "DEFAULT_ACTIVITY_RANGE_DAYS",
    "DEFAULT_DAILY_STATS_RANGE_DAYS",
    "MAX_ACTIVITY_RANGE_DAYS",
    "MAX_DAILY_STATS_RANGE_DAYS",
    "build_daily_activity_points",
    "build_daily_activity_stats_dto",
    "build_daily_stat_points",
    "resolve_activity_date_range",
    "resolve_daily_stats_date_range",
]
