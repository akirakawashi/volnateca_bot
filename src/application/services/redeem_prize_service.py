from dataclasses import dataclass
from enum import Enum

from application.common.dto.prize_redemption import (
    CreatePrizeRedemptionParams,
    PrizeLockedSnapshot,
    PrizeRedemptionRecord,
)
from application.common.dto.store import STORE_ALLOWED_PRIZE_TYPES
from application.common.redemption_code import generate_redemption_code
from application.interface.repositories.prize_redemptions import IPrizeRedemptionRepository
from application.interface.repositories.prizes import IPrizeRepository
from application.interface.repositories.transactions import ITransactionRepository
from application.interface.repositories.users import IUserRepository
from domain.enums.prize import PrizeStatus
from domain.enums.transaction import TransactionSource, TransactionType
from domain.services.wallet import WalletService


class RedeemPrizeOutcomeStatus(str, Enum):
    COMPLETED = "completed"
    IDEMPOTENT_REPLAY = "idempotent_replay"
    USER_NOT_REGISTERED = "user_not_registered"
    PRIZE_NOT_FOUND = "prize_not_found"
    PRIZE_NOT_AVAILABLE = "prize_not_available"
    SOLD_OUT = "sold_out"
    INSUFFICIENT_BALANCE = "insufficient_balance"
    LEVEL_LOCKED = "level_locked"


@dataclass(slots=True, frozen=True, kw_only=True)
class RedeemPrizeOutcome:
    status: RedeemPrizeOutcomeStatus
    vk_user_id: int
    users_id: int | None = None
    prizes_id: int | None = None
    prize_name: str | None = None
    prize_redemptions_id: int | None = None
    redemption_code: str | None = None
    points_spent: int = 0
    balance_points: int | None = None
    transactions_id: int | None = None


class RedeemPrizeService:
    """Единственная точка покупки приза в магазине."""

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

    async def redeem(
        self,
        *,
        vk_user_id: int,
        prizes_id: int,
        idempotency_key: str,
        user_comment: str | None = None,
    ) -> RedeemPrizeOutcome:
        replay = await self._idempotent_replay_if_exists(
            vk_user_id=vk_user_id,
            idempotency_key=idempotency_key,
        )
        if replay is not None:
            return replay

        snapshot = await self._users.get_balance_snapshot_for_update(vk_user_id=vk_user_id)
        if snapshot is None:
            return RedeemPrizeOutcome(
                status=RedeemPrizeOutcomeStatus.USER_NOT_REGISTERED,
                vk_user_id=vk_user_id,
                prizes_id=prizes_id,
            )

        replay = await self._idempotent_replay_if_exists(
            vk_user_id=vk_user_id,
            idempotency_key=idempotency_key,
        )
        if replay is not None:
            return replay

        prize = await self._prizes.get_for_update(prizes_id=prizes_id)
        if prize is None:
            return RedeemPrizeOutcome(
                status=RedeemPrizeOutcomeStatus.PRIZE_NOT_FOUND,
                vk_user_id=vk_user_id,
                users_id=snapshot.users_id,
                prizes_id=prizes_id,
                balance_points=snapshot.balance_points,
            )

        availability = self._check_availability(
            prize=prize,
            balance_points=snapshot.balance_points,
            current_level=snapshot.current_level,
        )
        if availability is not None:
            return RedeemPrizeOutcome(
                status=availability,
                vk_user_id=vk_user_id,
                users_id=snapshot.users_id,
                prizes_id=prizes_id,
                prize_name=prize.prize_name,
                balance_points=snapshot.balance_points,
            )

        try:
            spend = WalletService.spend(
                balance_before=snapshot.balance_points,
                spent_points_total_before=snapshot.spent_points_total,
                amount=prize.cost_points,
            )
        except ValueError:
            return RedeemPrizeOutcome(
                status=RedeemPrizeOutcomeStatus.INSUFFICIENT_BALANCE,
                vk_user_id=vk_user_id,
                users_id=snapshot.users_id,
                prizes_id=prizes_id,
                prize_name=prize.prize_name,
                balance_points=snapshot.balance_points,
            )

        if not await self._prizes.try_increment_claimed(prizes_id=prizes_id):
            return RedeemPrizeOutcome(
                status=RedeemPrizeOutcomeStatus.SOLD_OUT,
                vk_user_id=vk_user_id,
                users_id=snapshot.users_id,
                prizes_id=prizes_id,
                prize_name=prize.prize_name,
                balance_points=snapshot.balance_points,
            )

        transaction = await self._transactions.create(
            users_id=snapshot.users_id,
            tasks_id=None,
            prizes_id=prizes_id,
            transaction_type=TransactionType.SPEND,
            transaction_source=TransactionSource.PRIZE,
            amount=spend.amount,
            balance_before=spend.balance_before,
            balance_after=spend.balance_after,
            description=f"Списание за приз: {prize.prize_name}",
        )

        redemption_code = generate_redemption_code()
        redemption = await self._prize_redemptions.create(
            CreatePrizeRedemptionParams(
                users_id=snapshot.users_id,
                prizes_id=prizes_id,
                transactions_id=transaction.transactions_id,
                receive_type=prize.receive_type,
                redemption_code=redemption_code,
                idempotency_key=idempotency_key,
                points_spent=spend.amount,
                comment=user_comment,
            ),
        )

        await self._users.apply_spend(
            users_id=snapshot.users_id,
            balance_points=spend.balance_after,
            spent_points_total=spend.spent_points_total_after,
        )
        await self._prizes.sync_sold_out_status(prizes_id=prizes_id)

        return RedeemPrizeOutcome(
            status=RedeemPrizeOutcomeStatus.COMPLETED,
            vk_user_id=vk_user_id,
            users_id=snapshot.users_id,
            prizes_id=prizes_id,
            prize_name=prize.prize_name,
            prize_redemptions_id=redemption.prize_redemptions_id,
            redemption_code=redemption.redemption_code,
            points_spent=spend.amount,
            balance_points=spend.balance_after,
            transactions_id=transaction.transactions_id,
        )

    async def _idempotent_replay_if_exists(
        self,
        *,
        vk_user_id: int,
        idempotency_key: str,
    ) -> RedeemPrizeOutcome | None:
        existing = await self._prize_redemptions.get_by_idempotency_key(
            idempotency_key=idempotency_key,
        )
        if existing is None:
            return None
        return self.idempotent_replay_outcome(
            vk_user_id=vk_user_id,
            existing=existing,
        )

    @staticmethod
    def idempotent_replay_outcome(
        *,
        vk_user_id: int,
        existing: PrizeRedemptionRecord,
    ) -> RedeemPrizeOutcome:
        return RedeemPrizeOutcome(
            status=RedeemPrizeOutcomeStatus.IDEMPOTENT_REPLAY,
            vk_user_id=vk_user_id,
            users_id=existing.users_id,
            prizes_id=existing.prizes_id,
            prize_name=existing.prize_name,
            prize_redemptions_id=existing.prize_redemptions_id,
            redemption_code=existing.redemption_code,
            points_spent=existing.points_spent,
            transactions_id=existing.transactions_id,
        )

    @staticmethod
    def _check_availability(
        *,
        prize: PrizeLockedSnapshot,
        balance_points: int,
        current_level: int,
    ) -> RedeemPrizeOutcomeStatus | None:
        if not prize.is_active or prize.status == PrizeStatus.HIDDEN:
            return RedeemPrizeOutcomeStatus.PRIZE_NOT_AVAILABLE
        if prize.prize_type not in STORE_ALLOWED_PRIZE_TYPES:
            return RedeemPrizeOutcomeStatus.PRIZE_NOT_AVAILABLE
        if prize.status == PrizeStatus.SOLD_OUT or prize.quantity_claimed >= prize.quantity_total:
            return RedeemPrizeOutcomeStatus.SOLD_OUT
        if prize.required_level is not None and current_level < prize.required_level:
            return RedeemPrizeOutcomeStatus.LEVEL_LOCKED
        if balance_points < prize.cost_points:
            return RedeemPrizeOutcomeStatus.INSUFFICIENT_BALANCE
        return None


__all__ = [
    "RedeemPrizeOutcome",
    "RedeemPrizeOutcomeStatus",
    "RedeemPrizeService",
]
