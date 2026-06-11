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
    promo_codes: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdatePrizeCommand:
    """Частичное обновление приза. Поле меняется только если его имя есть в `fields`."""

    prizes_id: int
    fields: frozenset[str]
    prize_name: str | None = None
    description: str | None = None
    image_attachment: str | None = None
    status: PrizeStatus | None = None
    cost_points: int | None = None
    quantity_total: int | None = None
    required_level: int | None = None
    sort_order: int | None = None
    is_active: bool | None = None


__all__ = [
    "CreatePrizeCommand",
    "ListPrizesCommand",
    "UpdatePrizeCommand",
]
