from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum

from application.interface.repositories.prize_redemptions import IPrizeRedemptionRepository
from domain.enums.prize import PrizeRedemptionStatus


class FulfillRedemptionOutcomeStatus(str, Enum):
    COMPLETED = "completed"
    NOT_FOUND = "not_found"
    INVALID_STATUS = "invalid_status"


@dataclass(slots=True, frozen=True, kw_only=True)
class FulfillRedemptionOutcome:
    status: FulfillRedemptionOutcomeStatus
    prize_redemptions_id: int
    redemption_code: str | None = None


class FulfillRedemptionService:
    def __init__(self, prize_redemptions: IPrizeRedemptionRepository) -> None:
        self._prize_redemptions = prize_redemptions

    async def fulfill(
        self,
        *,
        prize_redemptions_id: int,
        comment: str | None = None,
    ) -> FulfillRedemptionOutcome:
        redemption = await self._prize_redemptions.get_for_update(
            prize_redemptions_id=prize_redemptions_id,
        )
        if redemption is None:
            return FulfillRedemptionOutcome(
                status=FulfillRedemptionOutcomeStatus.NOT_FOUND,
                prize_redemptions_id=prize_redemptions_id,
            )
        if redemption.prize_redemption_status != PrizeRedemptionStatus.RESERVED:
            return FulfillRedemptionOutcome(
                status=FulfillRedemptionOutcomeStatus.INVALID_STATUS,
                prize_redemptions_id=prize_redemptions_id,
                redemption_code=redemption.redemption_code,
            )

        updated = await self._prize_redemptions.mark_issued(
            prize_redemptions_id=prize_redemptions_id,
            issued_at=datetime.now(tz=UTC),
            comment=comment,
        )
        return FulfillRedemptionOutcome(
            status=FulfillRedemptionOutcomeStatus.COMPLETED,
            prize_redemptions_id=prize_redemptions_id,
            redemption_code=updated.redemption_code,
        )


__all__ = [
    "FulfillRedemptionOutcome",
    "FulfillRedemptionOutcomeStatus",
    "FulfillRedemptionService",
]
