from datetime import date

import pytest
from zoneinfo import ZoneInfo

from application.admin.services.daily_activity_stats import (
    build_daily_stat_points,
    resolve_daily_stats_date_range,
)

resolve_activity_date_range = resolve_daily_stats_date_range
build_daily_activity_points = build_daily_stat_points


def test_resolve_activity_date_range_defaults_to_30_days() -> None:
    tz = ZoneInfo("Europe/Moscow")
    from_date, to_date = resolve_activity_date_range(
        from_date=None,
        to_date=date(2026, 5, 30),
        project_timezone=tz,
    )
    assert to_date == date(2026, 5, 30)
    assert from_date == date(2026, 5, 1)


def test_resolve_activity_date_range_rejects_inverted_range() -> None:
    with pytest.raises(ValueError, match="from must be"):
        resolve_activity_date_range(
            from_date=date(2026, 5, 10),
            to_date=date(2026, 5, 1),
            project_timezone=ZoneInfo("Europe/Moscow"),
        )


def test_build_daily_activity_points_fills_missing_days_with_zero() -> None:
    points = build_daily_activity_points(
        from_date=date(2026, 5, 1),
        to_date=date(2026, 5, 3),
        values_by_day={date(2026, 5, 2): 4},
    )
    assert [(point.day, point.value) for point in points] == [
        (date(2026, 5, 1), 0),
        (date(2026, 5, 2), 4),
        (date(2026, 5, 3), 0),
    ]
