from dataclasses import dataclass

from application.admin.admin_rules import ADMIN_MAX_PAGE, ADMIN_REDEMPTIONS_PAGE_SIZE
from application.admin.dto.pagination import AdminListPageDTO, build_admin_list_page
from application.admin.dto.prize_redemption import PrizeRedemptionAdminDTO
from application.base_interactor import Interactor
from application.common.dto.prize_redemption import PrizeRedemptionRecord
from application.interface.repositories.prize_redemptions import IPrizeRedemptionRepository
from application.interface.uow import IUnitOfWork
from application.services.cancel_redemption_service import (
    CancelRedemptionOutcome,
    CancelRedemptionService,
)
from application.services.fulfill_redemption_service import (
    FulfillRedemptionOutcome,
    FulfillRedemptionService,
)
from domain.enums.prize import PrizeRedemptionStatus


@dataclass(slots=True, frozen=True, kw_only=True)
class ListPrizeRedemptionsCommand:
    status: PrizeRedemptionStatus | None = None
    prizes_id: int | None = None
    page: int = 1


@dataclass(slots=True, frozen=True, kw_only=True)
class GetPrizeRedemptionQueueCountCommand:
    pass


@dataclass(slots=True, frozen=True, kw_only=True)
class GetPrizeRedemptionCommand:
    prize_redemptions_id: int


@dataclass(slots=True, frozen=True, kw_only=True)
class GetPrizeRedemptionByCodeCommand:
    redemption_code: str


@dataclass(slots=True, frozen=True, kw_only=True)
class FulfillPrizeRedemptionCommand:
    prize_redemptions_id: int
    comment: str | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class CancelPrizeRedemptionCommand:
    prize_redemptions_id: int
    cancel_reason: str | None = None


class ListPrizeRedemptionsHandler(
    Interactor[ListPrizeRedemptionsCommand, AdminListPageDTO[PrizeRedemptionAdminDTO]],
):
    def __init__(self, prize_redemption_repository: IPrizeRedemptionRepository) -> None:
        self._prize_redemptions = prize_redemption_repository

    async def __call__(
        self,
        command_data: ListPrizeRedemptionsCommand,
    ) -> AdminListPageDTO[PrizeRedemptionAdminDTO]:
        page = max(1, min(command_data.page, ADMIN_MAX_PAGE))
        offset = (page - 1) * ADMIN_REDEMPTIONS_PAGE_SIZE
        records = await self._prize_redemptions.list_for_fulfillment(
            status=command_data.status,
            prizes_id=command_data.prizes_id,
            limit=ADMIN_REDEMPTIONS_PAGE_SIZE + 1,
            offset=offset,
        )
        items = tuple(to_prize_redemption_admin_dto(record) for record in records)
        return build_admin_list_page(
            page=page,
            page_size=ADMIN_REDEMPTIONS_PAGE_SIZE,
            fetched=items,
        )


class GetPrizeRedemptionQueueCountHandler(
    Interactor[GetPrizeRedemptionQueueCountCommand, int],
):
    def __init__(self, prize_redemption_repository: IPrizeRedemptionRepository) -> None:
        self._prize_redemptions = prize_redemption_repository

    async def __call__(
        self,
        _command_data: GetPrizeRedemptionQueueCountCommand,
    ) -> int:
        return await self._prize_redemptions.count_for_fulfillment(
            status=PrizeRedemptionStatus.RESERVED,
            prizes_id=None,
        )


class GetPrizeRedemptionHandler(
    Interactor[GetPrizeRedemptionCommand, PrizeRedemptionAdminDTO | None],
):
    def __init__(self, prize_redemption_repository: IPrizeRedemptionRepository) -> None:
        self._prize_redemptions = prize_redemption_repository

    async def __call__(
        self,
        command_data: GetPrizeRedemptionCommand,
    ) -> PrizeRedemptionAdminDTO | None:
        record = await self._prize_redemptions.get_by_id(
            prize_redemptions_id=command_data.prize_redemptions_id,
        )
        if record is None:
            return None
        return to_prize_redemption_admin_dto(record)


class GetPrizeRedemptionByCodeHandler(
    Interactor[GetPrizeRedemptionByCodeCommand, PrizeRedemptionAdminDTO | None],
):
    def __init__(self, prize_redemption_repository: IPrizeRedemptionRepository) -> None:
        self._prize_redemptions = prize_redemption_repository

    async def __call__(
        self,
        command_data: GetPrizeRedemptionByCodeCommand,
    ) -> PrizeRedemptionAdminDTO | None:
        record = await self._prize_redemptions.get_by_redemption_code(
            redemption_code=command_data.redemption_code,
        )
        if record is None:
            return None
        return to_prize_redemption_admin_dto(record)


class FulfillPrizeRedemptionHandler(
    Interactor[FulfillPrizeRedemptionCommand, FulfillRedemptionOutcome],
):
    def __init__(
        self,
        fulfill_redemption_service: FulfillRedemptionService,
        uow: IUnitOfWork,
    ) -> None:
        self._fulfill_redemption_service = fulfill_redemption_service
        self._uow = uow

    async def __call__(
        self,
        command_data: FulfillPrizeRedemptionCommand,
    ) -> FulfillRedemptionOutcome:
        outcome = await self._fulfill_redemption_service.fulfill(
            prize_redemptions_id=command_data.prize_redemptions_id,
            comment=command_data.comment,
        )
        await self._uow.commit()
        return outcome


class CancelPrizeRedemptionHandler(
    Interactor[CancelPrizeRedemptionCommand, CancelRedemptionOutcome],
):
    def __init__(
        self,
        cancel_redemption_service: CancelRedemptionService,
        uow: IUnitOfWork,
    ) -> None:
        self._cancel_redemption_service = cancel_redemption_service
        self._uow = uow

    async def __call__(
        self,
        command_data: CancelPrizeRedemptionCommand,
    ) -> CancelRedemptionOutcome:
        outcome = await self._cancel_redemption_service.cancel(
            prize_redemptions_id=command_data.prize_redemptions_id,
            cancel_reason=command_data.cancel_reason,
        )
        await self._uow.commit()
        return outcome


def to_prize_redemption_admin_dto(record: PrizeRedemptionRecord) -> PrizeRedemptionAdminDTO:
    return PrizeRedemptionAdminDTO(
        prize_redemptions_id=record.prize_redemptions_id,
        users_id=record.users_id,
        vk_user_id=record.vk_user_id,
        prizes_id=record.prizes_id,
        prize_name=record.prize_name or "",
        transactions_id=record.transactions_id,
        refund_transactions_id=record.refund_transactions_id,
        prize_redemption_status=record.prize_redemption_status,
        receive_type=record.receive_type,
        redemption_code=record.redemption_code,
        points_spent=record.points_spent,
        comment=record.comment,
        issued_at=record.issued_at,
        canceled_at=record.canceled_at,
        cancel_reason=record.cancel_reason,
        created_at=record.created_at,
        promo_code=record.promo_code,
    )


__all__ = [
    "to_prize_redemption_admin_dto",
    "CancelPrizeRedemptionCommand",
    "CancelPrizeRedemptionHandler",
    "FulfillPrizeRedemptionCommand",
    "FulfillPrizeRedemptionHandler",
    "GetPrizeRedemptionByCodeCommand",
    "GetPrizeRedemptionByCodeHandler",
    "GetPrizeRedemptionCommand",
    "GetPrizeRedemptionHandler",
    "GetPrizeRedemptionQueueCountCommand",
    "GetPrizeRedemptionQueueCountHandler",
    "ListPrizeRedemptionsCommand",
    "ListPrizeRedemptionsHandler",
]
