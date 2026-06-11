from dataclasses import dataclass
from datetime import datetime

from domain.enums.prize import PrizePromoCodeStatus


@dataclass(slots=True, frozen=True, kw_only=True)
class PrizePromoCodeRecord:
    prize_promo_codes_id: int
    prizes_id: int
    promo_code: str
    status: PrizePromoCodeStatus
    prize_redemptions_id: int | None
    assigned_to_users_id: int | None
    assigned_at: datetime | None


@dataclass(slots=True, frozen=True, kw_only=True)
class PrizePromoCodeStats:
    prizes_id: int
    total_codes: int
    available_codes: int
    assigned_codes: int
    void_codes: int


@dataclass(slots=True, frozen=True, kw_only=True)
class PrizePromoCodeBulkCreateResult:
    prizes_id: int
    created: int
    duplicates: int
    total_codes: int
    available_codes: int
    assigned_codes: int
    void_codes: int


def normalize_prize_promo_code(value: str) -> str:
    """Нормализует промокод партнёрского приза для хранения и сравнения."""

    return "".join(value.split()).upper()


def normalize_prize_promo_codes(values: tuple[str, ...]) -> tuple[str, ...]:
    """Возвращает непустые уникальные коды с сохранением порядка."""

    seen: set[str] = set()
    normalized: list[str] = []
    for value in values:
        code = normalize_prize_promo_code(value)
        if not code or code in seen:
            continue
        seen.add(code)
        normalized.append(code)
    return tuple(normalized)


__all__ = [
    "PrizePromoCodeBulkCreateResult",
    "PrizePromoCodeRecord",
    "PrizePromoCodeStats",
    "normalize_prize_promo_code",
    "normalize_prize_promo_codes",
]
