from abc import ABC, abstractmethod

from application.common.dto.prize_redemption import PrizeLockedSnapshot
from application.common.dto.store import StorePrizeSnapshot
from domain.enums.prize import PrizeType


class IPrizeRepository(ABC):
    @abstractmethod
    async def list_store_prizes(
        self,
        *,
        prize_types: tuple[PrizeType, ...],
        limit: int,
        offset: int,
    ) -> tuple[StorePrizeSnapshot, ...]:
        raise NotImplementedError

    @abstractmethod
    async def count_store_prizes(
        self,
        *,
        prize_types: tuple[PrizeType, ...],
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def get_store_prize(
        self,
        *,
        prizes_id: int,
    ) -> StorePrizeSnapshot | None:
        raise NotImplementedError

    @abstractmethod
    async def get_for_update(
        self,
        *,
        prizes_id: int,
    ) -> PrizeLockedSnapshot | None:
        raise NotImplementedError

    @abstractmethod
    async def try_increment_claimed(
        self,
        *,
        prizes_id: int,
    ) -> bool:
        """Атомарно увеличивает quantity_claimed, если остаток > 0."""

        raise NotImplementedError

    @abstractmethod
    async def decrement_claimed(
        self,
        *,
        prizes_id: int,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def sync_sold_out_status(
        self,
        *,
        prizes_id: int,
    ) -> None:
        """Выставляет sold_out или available по фактическому остатку."""

        raise NotImplementedError


__all__ = ["IPrizeRepository"]
