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


@dataclass(slots=True, frozen=True, kw_only=True)
class AccrualSourceSegmentDTO:
    source: str
    value: int


@dataclass(slots=True, frozen=True, kw_only=True)
class AccrualSourcesStatsDTO:
    timezone: str
    from_date: date
    to_date: date
    total: int
    segments: tuple[AccrualSourceSegmentDTO, ...]


__all__ = [
    "AccrualSourceSegmentDTO",
    "AccrualSourcesStatsDTO",
    "DailyAccrualPointsStatsDTO",
    "DailyActivityStatsDTO",
    "DailyNewUsersStatsDTO",
    "DailyStatPointDTO",
]
