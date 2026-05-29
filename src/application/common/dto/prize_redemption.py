from dataclasses import dataclass
from datetime import datetime

from domain.enums.prize import (
    PrizeReceiveType,
    PrizeRedemptionStatus,
    PrizeStatus,
    PrizeType,
)


@dataclass(slots=True, frozen=True, kw_only=True)
class PrizeLockedSnapshot:
    """Снимок приза под блокировкой FOR UPDATE."""

    prizes_id: int
    code: str
    prize_name: str
    prize_type: PrizeType
    receive_type: PrizeReceiveType
    status: PrizeStatus
    cost_points: int
    quantity_total: int
    quantity_claimed: int
    required_level: int | None
    is_active: bool


@dataclass(slots=True, frozen=True, kw_only=True)
class PrizeRedemptionRecord:
    prize_redemptions_id: int
    users_id: int
    prizes_id: int
    transactions_id: int
    prize_redemption_status: PrizeRedemptionStatus
    receive_type: PrizeReceiveType
    redemption_code: str
    idempotency_key: str
    points_spent: int
    comment: str | None
    issued_at: datetime | None
    canceled_at: datetime | None
    cancel_reason: str | None
    refund_transactions_id: int | None
    created_at: datetime
    prize_name: str | None = None
    vk_user_id: int | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class CreatePrizeRedemptionParams:
    users_id: int
    prizes_id: int
    transactions_id: int
    receive_type: PrizeReceiveType
    redemption_code: str
    idempotency_key: str
    points_spent: int
    comment: str | None = None


__all__ = [
    "CreatePrizeRedemptionParams",
    "PrizeLockedSnapshot",
    "PrizeRedemptionRecord",
]
