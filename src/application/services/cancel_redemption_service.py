from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum

from application.interface.repositories.prize_redemptions import IPrizeRedemptionRepository
from application.interface.repositories.prizes import IPrizeRepository
from application.interface.repositories.transactions import ITransactionRepository
from application.interface.repositories.users import IUserRepository
from domain.enums.prize import PrizeRedemptionStatus
from domain.enums.transaction import TransactionSource, TransactionType
from domain.services.wallet import WalletService


class CancelRedemptionOutcomeStatus(str, Enum):
    COMPLETED = "completed"
    NOT_FOUND = "not_found"
    INVALID_STATUS = "invalid_status"
    USER_NOT_FOUND = "user_not_found"


@dataclass(slots=True, frozen=True, kw_only=True)
class CancelRedemptionOutcome:
    status: CancelRedemptionOutcomeStatus
    prize_redemptions_id: int
    refund_transactions_id: int | None = None


class CancelRedemptionService:
    def __init__(
        self,
        users: IUserRepository,
        prizes: IPrizeRepository,
        prize_redemptions: IPrizeRedemptionRepository,
        transactions: ITransactionRepository,
    ) -> None:
        self._users = users
        self._prizes = prizes
        self._prize_redemptions = prize_redemptions
        self._transactions = transactions

    async def cancel(
        self,
        *,
        prize_redemptions_id: int,
        cancel_reason: str | None = None,
    ) -> CancelRedemptionOutcome:
        redemption = await self._prize_redemptions.get_for_update(
            prize_redemptions_id=prize_redemptions_id,
        )
        if redemption is None:
            return CancelRedemptionOutcome(
                status=CancelRedemptionOutcomeStatus.NOT_FOUND,
                prize_redemptions_id=prize_redemptions_id,
            )
        if redemption.prize_redemption_status != PrizeRedemptionStatus.RESERVED:
            return CancelRedemptionOutcome(
                status=CancelRedemptionOutcomeStatus.INVALID_STATUS,
                prize_redemptions_id=prize_redemptions_id,
            )

        snapshot = await self._users.get_balance_snapshot_by_users_id_for_update(
            users_id=redemption.users_id,
        )
        if snapshot is None:
            return CancelRedemptionOutcome(
                status=CancelRedemptionOutcomeStatus.USER_NOT_FOUND,
                prize_redemptions_id=prize_redemptions_id,
            )

        refund = WalletService.refund_spend(
            balance_before=snapshot.balance_points,
            spent_points_total_before=snapshot.spent_points_total,
            amount=redemption.points_spent,
        )

        refund_transaction = await self._transactions.create(
            users_id=redemption.users_id,
            tasks_id=None,
            prizes_id=redemption.prizes_id,
            transaction_type=TransactionType.ACCRUAL,
            transaction_source=TransactionSource.PRIZE,
            amount=refund.amount,
            balance_before=refund.balance_before,
            balance_after=refund.balance_after,
            description=f"Возврат за отмену заявки {redemption.redemption_code}",
        )

        await self._prize_redemptions.mark_canceled(
            prize_redemptions_id=prize_redemptions_id,
            canceled_at=datetime.now(tz=UTC),
            cancel_reason=cancel_reason,
            refund_transactions_id=refund_transaction.transactions_id,
        )
        await self._prizes.decrement_claimed(prizes_id=redemption.prizes_id)
        await self._prizes.sync_sold_out_status(prizes_id=redemption.prizes_id)
        await self._users.apply_refund(
            users_id=redemption.users_id,
            balance_points=refund.balance_after,
            spent_points_total=refund.spent_points_total_after,
        )

        return CancelRedemptionOutcome(
            status=CancelRedemptionOutcomeStatus.COMPLETED,
            prize_redemptions_id=prize_redemptions_id,
            refund_transactions_id=refund_transaction.transactions_id,
        )


__all__ = [
    "CancelRedemptionOutcome",
    "CancelRedemptionOutcomeStatus",
    "CancelRedemptionService",
]
