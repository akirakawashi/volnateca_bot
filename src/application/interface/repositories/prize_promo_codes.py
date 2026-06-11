from abc import ABC, abstractmethod
from datetime import datetime

from application.common.dto.prize_promo_code import (
    PrizePromoCodeBulkCreateResult,
    PrizePromoCodeRecord,
    PrizePromoCodeStats,
)


class IPrizePromoCodeRepository(ABC):
    @abstractmethod
    async def get_available_for_update(
        self,
        *,
        prizes_id: int,
    ) -> PrizePromoCodeRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def assign_to_redemption(
        self,
        *,
        prize_promo_codes_id: int,
        prize_redemptions_id: int,
        users_id: int,
        assigned_at: datetime,
    ) -> PrizePromoCodeRecord:
        raise NotImplementedError

    @abstractmethod
    async def get_stats(
        self,
        *,
        prizes_id: int,
    ) -> PrizePromoCodeStats:
        raise NotImplementedError

    @abstractmethod
    async def bulk_create(
        self,
        *,
        prizes_id: int,
        promo_codes: tuple[str, ...],
    ) -> PrizePromoCodeBulkCreateResult | None:
        raise NotImplementedError


__all__ = ["IPrizePromoCodeRepository"]
