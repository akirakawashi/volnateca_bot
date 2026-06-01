from abc import ABC, abstractmethod
from datetime import datetime

from application.common.dto.prize_redemption import CreatePrizeRedemptionParams, PrizeRedemptionRecord
from domain.enums.prize import PrizeRedemptionStatus


class IPrizeRedemptionRepository(ABC):
    @abstractmethod
    async def get_by_idempotency_key(
        self,
        *,
        idempotency_key: str,
    ) -> PrizeRedemptionRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(
        self,
        *,
        prize_redemptions_id: int,
    ) -> PrizeRedemptionRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_redemption_code(
        self,
        *,
        redemption_code: str,
    ) -> PrizeRedemptionRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def get_for_update(
        self,
        *,
        prize_redemptions_id: int,
    ) -> PrizeRedemptionRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def create(
        self,
        params: CreatePrizeRedemptionParams,
    ) -> PrizeRedemptionRecord:
        raise NotImplementedError

    @abstractmethod
    async def list_by_user(
        self,
        *,
        users_id: int,
        limit: int,
        offset: int,
    ) -> tuple[PrizeRedemptionRecord, ...]:
        raise NotImplementedError

    @abstractmethod
    async def list_for_fulfillment(
        self,
        *,
        status: PrizeRedemptionStatus | None,
        prizes_id: int | None,
        limit: int,
        offset: int,
    ) -> tuple[PrizeRedemptionRecord, ...]:
        raise NotImplementedError

    @abstractmethod
    async def mark_issued(
        self,
        *,
        prize_redemptions_id: int,
        issued_at: datetime,
        comment: str | None,
    ) -> PrizeRedemptionRecord:
        raise NotImplementedError

    @abstractmethod
    async def mark_canceled(
        self,
        *,
        prize_redemptions_id: int,
        canceled_at: datetime,
        cancel_reason: str | None,
        refund_transactions_id: int,
    ) -> PrizeRedemptionRecord:
        raise NotImplementedError


__all__ = ["IPrizeRedemptionRepository"]
