from dataclasses import dataclass
from enum import Enum

from domain.enums.prize import PrizeStatus, PrizeType


STORE_PAGE_SIZE = 3
STORE_ALLOWED_PRIZE_TYPES: tuple[PrizeType, ...] = (
    PrizeType.MERCH,
    PrizeType.PARTNER,
    PrizeType.SUPER_PRIZE,
)


class StoreSection(str, Enum):
    ALL = "all"
    MERCH = "merch"
    PARTNER = "partner"
    SUPER_PRIZE = "super_prize"

    @property
    def label(self) -> str:
        if self is StoreSection.ALL:
            return "Все"
        if self is StoreSection.MERCH:
            return "Мерч"
        if self is StoreSection.PARTNER:
            return "Партнёры"
        return "Суперпризы"

    @property
    def prize_types(self) -> tuple[PrizeType, ...]:
        if self is StoreSection.ALL:
            return STORE_ALLOWED_PRIZE_TYPES
        return (PrizeType(self.value),)


class StorePrizeUserState(str, Enum):
    AVAILABLE = "available"
    INSUFFICIENT_BALANCE = "insufficient_balance"
    LEVEL_LOCKED = "level_locked"
    SOLD_OUT = "sold_out"


@dataclass(slots=True, frozen=True, kw_only=True)
class StorePrizeSnapshot:
    prizes_id: int
    prize_name: str
    description: str | None
    image_attachment: str | None
    prize_type: PrizeType
    status: PrizeStatus
    cost_points: int
    quantity_total: int
    quantity_claimed: int
    sort_order: int
    required_level: int | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class StorePrizeView:
    prizes_id: int
    prize_name: str
    description: str | None
    image_attachment: str | None
    prize_type: PrizeType
    cost_points: int
    quantity_total: int
    quantity_claimed: int
    quantity_remaining: int
    required_level: int | None
    user_state: StorePrizeUserState
    missing_points: int


@dataclass(slots=True, frozen=True, kw_only=True)
class StorePaginationDTO:
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_previous: bool
    has_next: bool


@dataclass(slots=True, frozen=True, kw_only=True)
class StoreCatalogDTO:
    section: StoreSection
    balance_points: int
    current_level: int
    pagination: StorePaginationDTO
    prizes: tuple[StorePrizeView, ...]


@dataclass(slots=True, frozen=True, kw_only=True)
class StorePrizeCardDTO:
    section: StoreSection
    page: int
    balance_points: int
    current_level: int
    prize: StorePrizeView | None


def list_store_sections() -> tuple[StoreSection, ...]:
    return (
        StoreSection.ALL,
        StoreSection.MERCH,
        StoreSection.PARTNER,
        StoreSection.SUPER_PRIZE,
    )


__all__ = [
    "STORE_ALLOWED_PRIZE_TYPES",
    "STORE_PAGE_SIZE",
    "StoreCatalogDTO",
    "StorePaginationDTO",
    "StorePrizeCardDTO",
    "StorePrizeSnapshot",
    "StorePrizeUserState",
    "StorePrizeView",
    "StoreSection",
    "list_store_sections",
]
