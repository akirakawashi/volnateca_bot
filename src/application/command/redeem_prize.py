from dataclasses import dataclass

from application.base_interactor import Interactor
from application.interface.uow import IUnitOfWork
from application.services.redeem_prize_service import RedeemPrizeOutcome, RedeemPrizeService


@dataclass(slots=True, frozen=True, kw_only=True)
class RedeemPrizeCommand:
    vk_user_id: int
    prizes_id: int
    idempotency_key: str
    user_comment: str | None = None


class RedeemPrizeHandler(Interactor[RedeemPrizeCommand, RedeemPrizeOutcome]):
    def __init__(
        self,
        redeem_prize_service: RedeemPrizeService,
        uow: IUnitOfWork,
    ) -> None:
        self._redeem_prize_service = redeem_prize_service
        self._uow = uow

    async def __call__(self, command_data: RedeemPrizeCommand) -> RedeemPrizeOutcome:
        outcome = await self._redeem_prize_service.redeem(
            vk_user_id=command_data.vk_user_id,
            prizes_id=command_data.prizes_id,
            idempotency_key=command_data.idempotency_key,
            user_comment=command_data.user_comment,
        )
        await self._uow.commit()
        return outcome


__all__ = ["RedeemPrizeCommand", "RedeemPrizeHandler"]
