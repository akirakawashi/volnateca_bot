from dataclasses import dataclass

from application.common.dto.prize_redemption import PrizeRedemptionRecord


@dataclass(frozen=True, kw_only=True)
class PrizeRedemptionIdempotencyConflict(Exception):
    """Параллельный redeem с тем же idempotency_key уже закоммитил заявку."""

    existing: PrizeRedemptionRecord


__all__ = ["PrizeRedemptionIdempotencyConflict"]
