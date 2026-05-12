from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class AchievementRecord:
    achievements_id: int
    code: str
    achievement_name: str
    points: int


class IAchievementRepository(ABC):
    @abstractmethod
    async def get_by_code(self, code: str) -> AchievementRecord | None:
        """Возвращает запись достижения по стабильному коду."""
        raise NotImplementedError

    @abstractmethod
    async def is_awarded(
        self,
        *,
        users_id: int,
        achievements_id: int,
        achievement_key: str,
    ) -> bool:
        """Возвращает True, если пользователь уже получил достижение за период."""
        raise NotImplementedError

    @abstractmethod
    async def count_awarded_keys_by_code(
        self,
        *,
        users_id: int,
        achievement_code: str,
        achievement_keys: tuple[str, ...],
    ) -> int:
        """Возвращает количество выданных пользователю ключей достижения."""
        raise NotImplementedError

    @abstractmethod
    async def award_if_not_exists(
        self,
        *,
        users_id: int,
        achievements_id: int,
        transactions_id: int,
        achievement_key: str,
        points: int,
    ) -> bool:
        """Создаёт запись в user_achievements, если ещё не выдавалась.

        Возвращает True если достижение выдано впервые, False если уже было.
        Идемпотентность обеспечивается уникальным ограничением
        (users_id, achievements_id, achievement_key).
        """
        raise NotImplementedError


__all__ = ["AchievementRecord", "IAchievementRepository"]
