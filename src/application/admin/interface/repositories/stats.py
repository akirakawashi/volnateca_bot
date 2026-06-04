from abc import ABC, abstractmethod
from datetime import date
from zoneinfo import ZoneInfo

from domain.enums.transaction import TransactionSource


class IStatsAdminRepository(ABC):
    @abstractmethod
    async def count_daily_active_users_by_accrual(
        self,
        *,
        from_date: date,
        to_date: date,
        project_timezone: ZoneInfo,
    ) -> dict[date, int]:
        """Distinct users with at least one accrual per calendar day in project timezone."""
        raise NotImplementedError

    @abstractmethod
    async def count_daily_new_users(
        self,
        *,
        from_date: date,
        to_date: date,
        project_timezone: ZoneInfo,
    ) -> dict[date, int]:
        """New bot registrations per calendar day in project timezone."""
        raise NotImplementedError

    @abstractmethod
    async def sum_daily_accrual_points(
        self,
        *,
        from_date: date,
        to_date: date,
        project_timezone: ZoneInfo,
    ) -> dict[date, int]:
        """Total accrual points issued per calendar day in project timezone."""
        raise NotImplementedError

    @abstractmethod
    async def sum_accrual_points_by_source(
        self,
        *,
        from_date: date,
        to_date: date,
        project_timezone: ZoneInfo,
    ) -> dict[TransactionSource, int]:
        """Total accrual points grouped by transaction source for the date range."""
        raise NotImplementedError


__all__ = ["IStatsAdminRepository"]
