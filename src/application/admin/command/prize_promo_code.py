from dataclasses import dataclass

from application.base_interactor import Interactor
from application.common.dto.prize_promo_code import PrizePromoCodeBulkCreateResult
from application.interface.repositories.prize_promo_codes import IPrizePromoCodeRepository
from application.interface.uow import IUnitOfWork


@dataclass(slots=True, frozen=True, kw_only=True)
class AddPrizePromoCodesCommand:
    prizes_id: int
    promo_codes: tuple[str, ...]


class AddPrizePromoCodesHandler(
    Interactor[AddPrizePromoCodesCommand, PrizePromoCodeBulkCreateResult | None],
):
    def __init__(
        self,
        prize_promo_code_repository: IPrizePromoCodeRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._prize_promo_codes = prize_promo_code_repository
        self._uow = uow

    async def __call__(
        self,
        command_data: AddPrizePromoCodesCommand,
    ) -> PrizePromoCodeBulkCreateResult | None:
        result = await self._prize_promo_codes.bulk_create(
            prizes_id=command_data.prizes_id,
            promo_codes=command_data.promo_codes,
        )
        if result is None:
            return None
        await self._uow.commit()
        return result


__all__ = [
    "AddPrizePromoCodesCommand",
    "AddPrizePromoCodesHandler",
]
