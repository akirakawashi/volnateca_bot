from dataclasses import dataclass
from datetime import datetime

from domain.enums.prize import PrizeReceiveType, PrizeRedemptionStatus


@dataclass(slots=True, frozen=True, kw_only=True)
class PrizeRedemptionAdminDTO:
    prize_redemptions_id: int
    users_id: int
    vk_user_id: int | None
    prizes_id: int
    prize_name: str
    transactions_id: int
    refund_transactions_id: int | None
    prize_redemption_status: PrizeRedemptionStatus
    receive_type: PrizeReceiveType
    redemption_code: str
    points_spent: int
    comment: str | None
    issued_at: datetime | None
    canceled_at: datetime | None
    cancel_reason: str | None
    created_at: datetime


__all__ = ["PrizeRedemptionAdminDTO"]
