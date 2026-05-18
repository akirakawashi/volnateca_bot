from abc import ABC, abstractmethod

from application.common.dto.store import StorePrizeSnapshot
from domain.enums.prize import PrizeType


class IPrizeRepository(ABC):
    @abstractmethod
    async def list_store_prizes(
        self,
        *,
        prize_types: tuple[PrizeType, ...],
    ) -> tuple[StorePrizeSnapshot, ...]:
        raise NotImplementedError

    @abstractmethod
    async def get_store_prize(
        self,
        *,
        prizes_id: int,
    ) -> StorePrizeSnapshot | None:
        raise NotImplementedError


__all__ = ["IPrizeRepository"]
