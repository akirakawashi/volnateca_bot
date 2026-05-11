from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass(slots=True, frozen=True, kw_only=True)
class UserDailyActivityRecord:
    users_id: int
    activity_date: date
    streak_days: int


class IUserDailyActivityRepository(ABC):
    @abstractmethod
    async def get_by_user_and_date(
        self,
        *,
        users_id: int,
        activity_date: date,
    ) -> UserDailyActivityRecord | None:
        """Возвращает активность пользователя за конкретный день."""
        raise NotImplementedError

    @abstractmethod
    async def create_if_not_exists(
        self,
        *,
        users_id: int,
        activity_date: date,
        streak_days: int,
    ) -> tuple[UserDailyActivityRecord, bool]:
        """Фиксирует активность дня.

        Возвращает запись и True, если день создан впервые. Если активность
        за этот день уже есть, возвращает существующую запись и False.
        """
        raise NotImplementedError


__all__ = ["IUserDailyActivityRepository", "UserDailyActivityRecord"]
