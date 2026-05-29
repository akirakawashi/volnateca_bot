from dataclasses import dataclass

from application.base_interactor import Interactor
from application.common.dto.prize_redemption import PrizeRedemptionRecord
from application.interface.repositories.prize_redemptions import IPrizeRedemptionRepository

USER_REDEMPTIONS_PAGE_SIZE = 10


@dataclass(slots=True, frozen=True, kw_only=True)
class ListUserRedemptionsCommand:
    users_id: int
    page: int = 1


@dataclass(slots=True, frozen=True, kw_only=True)
class ListUserRedemptionsDTO:
    page: int
    has_previous: bool
    has_next: bool
    redemptions: tuple[PrizeRedemptionRecord, ...]


class ListUserRedemptionsHandler(Interactor[ListUserRedemptionsCommand, ListUserRedemptionsDTO]):
    def __init__(self, prize_redemption_repository: IPrizeRedemptionRepository) -> None:
        self._prize_redemptions = prize_redemption_repository

    async def __call__(self, command_data: ListUserRedemptionsCommand) -> ListUserRedemptionsDTO:
        page = max(1, command_data.page)
        offset = (page - 1) * USER_REDEMPTIONS_PAGE_SIZE
        fetched = await self._prize_redemptions.list_by_user(
            users_id=command_data.users_id,
            limit=USER_REDEMPTIONS_PAGE_SIZE + 1,
            offset=offset,
        )
        has_next = len(fetched) > USER_REDEMPTIONS_PAGE_SIZE
        return ListUserRedemptionsDTO(
            page=page,
            has_previous=page > 1,
            has_next=has_next,
            redemptions=fetched[:USER_REDEMPTIONS_PAGE_SIZE],
        )


__all__ = [
    "ListUserRedemptionsCommand",
    "ListUserRedemptionsDTO",
    "ListUserRedemptionsHandler",
    "USER_REDEMPTIONS_PAGE_SIZE",
]
