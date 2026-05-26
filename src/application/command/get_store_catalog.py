from dataclasses import dataclass

from application.base_interactor import Interactor
from application.common.dto.store import (
    STORE_PAGE_SIZE,
    StoreCatalogDTO,
    StorePaginationDTO,
    StorePrizeCardDTO,
    StorePrizeSnapshot,
    StorePrizeUserState,
    StorePrizeView,
    StoreSection,
)
from application.interface.repositories.prizes import IPrizeRepository
from domain.enums.prize import PrizeStatus


@dataclass(slots=True, frozen=True, kw_only=True)
class GetStoreCatalogCommand:
    balance_points: int
    current_level: int
    section: StoreSection = StoreSection.ALL
    page: int = 1


@dataclass(slots=True, frozen=True, kw_only=True)
class GetStorePrizeCardCommand:
    prizes_id: int
    balance_points: int
    current_level: int
    section: StoreSection = StoreSection.ALL
    page: int = 1


class GetStoreCatalogHandler(Interactor[GetStoreCatalogCommand, StoreCatalogDTO]):
    def __init__(self, prize_repository: IPrizeRepository) -> None:
        self.prize_repository = prize_repository

    async def __call__(self, command_data: GetStoreCatalogCommand) -> StoreCatalogDTO:
        prize_types = command_data.section.prize_types
        total_items = await self.prize_repository.count_store_prizes(prize_types=prize_types)
        total_pages = max(1, (total_items + STORE_PAGE_SIZE - 1) // STORE_PAGE_SIZE)
        page = _normalize_page(page=command_data.page, total_pages=total_pages)
        page_items: tuple[StorePrizeSnapshot, ...] = ()
        if total_items > 0:
            start = (page - 1) * STORE_PAGE_SIZE
            page_items = await self.prize_repository.list_store_prizes(
                prize_types=prize_types,
                limit=STORE_PAGE_SIZE,
                offset=start,
            )

        return StoreCatalogDTO(
            section=command_data.section,
            balance_points=command_data.balance_points,
            current_level=command_data.current_level,
            pagination=StorePaginationDTO(
                page=page,
                page_size=STORE_PAGE_SIZE,
                total_items=total_items,
                total_pages=total_pages,
                has_previous=page > 1,
                has_next=page < total_pages,
            ),
            prizes=tuple(
                _build_store_prize_view(
                    prize=prize,
                    balance_points=command_data.balance_points,
                    current_level=command_data.current_level,
                )
                for prize in page_items
            ),
        )


class GetStorePrizeCardHandler(Interactor[GetStorePrizeCardCommand, StorePrizeCardDTO]):
    def __init__(self, prize_repository: IPrizeRepository) -> None:
        self.prize_repository = prize_repository

    async def __call__(self, command_data: GetStorePrizeCardCommand) -> StorePrizeCardDTO:
        prize = await self.prize_repository.get_store_prize(prizes_id=command_data.prizes_id)
        return StorePrizeCardDTO(
            section=command_data.section,
            page=max(1, command_data.page),
            balance_points=command_data.balance_points,
            current_level=command_data.current_level,
            prize=(
                _build_store_prize_view(
                    prize=prize,
                    balance_points=command_data.balance_points,
                    current_level=command_data.current_level,
                )
                if prize is not None
                else None
            ),
        )


def _build_store_prize_view(
    *,
    prize: StorePrizeSnapshot,
    balance_points: int,
    current_level: int,
) -> StorePrizeView:
    quantity_remaining = (
        None if prize.quantity_total is None else max(0, prize.quantity_total - prize.quantity_claimed)
    )
    missing_points = max(0, prize.cost_points - balance_points)

    return StorePrizeView(
        prizes_id=prize.prizes_id,
        prize_name=prize.prize_name,
        description=prize.description,
        image_attachment=prize.image_attachment,
        prize_type=prize.prize_type,
        cost_points=prize.cost_points,
        quantity_total=prize.quantity_total,
        quantity_claimed=prize.quantity_claimed,
        quantity_remaining=quantity_remaining,
        required_level=prize.required_level,
        user_state=_resolve_store_prize_user_state(
            prize=prize,
            balance_points=balance_points,
            current_level=current_level,
        ),
        missing_points=missing_points,
    )


def _resolve_store_prize_user_state(
    *,
    prize: StorePrizeSnapshot,
    balance_points: int,
    current_level: int,
) -> StorePrizeUserState:
    if prize.status == PrizeStatus.SOLD_OUT:
        return StorePrizeUserState.SOLD_OUT
    if prize.quantity_total is not None and prize.quantity_claimed >= prize.quantity_total:
        return StorePrizeUserState.SOLD_OUT
    if prize.required_level is not None and current_level < prize.required_level:
        return StorePrizeUserState.LEVEL_LOCKED
    if balance_points < prize.cost_points:
        return StorePrizeUserState.INSUFFICIENT_BALANCE
    return StorePrizeUserState.AVAILABLE


def _normalize_page(*, page: int, total_pages: int) -> int:
    if page < 1:
        return 1
    if page > total_pages:
        return total_pages
    return page


__all__ = [
    "GetStoreCatalogCommand",
    "GetStoreCatalogHandler",
    "GetStorePrizeCardCommand",
    "GetStorePrizeCardHandler",
]
