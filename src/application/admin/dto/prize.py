from dataclasses import dataclass

from domain.enums.prize import PrizeReceiveType, PrizeStatus, PrizeType


@dataclass(slots=True, frozen=True, kw_only=True)
class ListPrizesCommand:
    pass


@dataclass(slots=True, frozen=True, kw_only=True)
class CreatePrizeCommand:
    prize_name: str
    description: str | None
    image_attachment: str | None
    prize_type: PrizeType
    receive_type: PrizeReceiveType
    status: PrizeStatus
    cost_points: int
    quantity_total: int
    required_level: int | None
    sort_order: int
    is_active: bool


@dataclass(slots=True, frozen=True, kw_only=True)
class PrizeAdminDTO:
    prizes_id: int
    code: str
    prize_name: str
    description: str | None
    image_attachment: str | None
    prize_type: PrizeType
    receive_type: PrizeReceiveType
    status: PrizeStatus
    cost_points: int
    quantity_total: int
    quantity_claimed: int
    required_level: int | None
    sort_order: int
    is_active: bool


__all__ = [
    "CreatePrizeCommand",
    "ListPrizesCommand",
    "PrizeAdminDTO",
]
