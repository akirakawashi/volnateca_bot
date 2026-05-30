from dataclasses import dataclass
from datetime import date


@dataclass(slots=True, frozen=True, kw_only=True)
class DailyStatPointDTO:
    day: date
    value: int


@dataclass(slots=True, frozen=True, kw_only=True)
class DailyActivityStatsDTO:
    timezone: str
    from_date: date
    to_date: date
    points: tuple[DailyStatPointDTO, ...]


@dataclass(slots=True, frozen=True, kw_only=True)
class DailyNewUsersStatsDTO:
    timezone: str
    from_date: date
    to_date: date
    points: tuple[DailyStatPointDTO, ...]


@dataclass(slots=True, frozen=True, kw_only=True)
class DailyAccrualPointsStatsDTO:
    timezone: str
    from_date: date
    to_date: date
    points: tuple[DailyStatPointDTO, ...]


__all__ = [
    "DailyAccrualPointsStatsDTO",
    "DailyActivityStatsDTO",
    "DailyNewUsersStatsDTO",
    "DailyStatPointDTO",
]
