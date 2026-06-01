from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class CreatedTaskPromoCodeTaskDTO:
    tasks_id: int
    code: str
    task_name: str
    promo_codes_total: int


__all__ = [
    "CreatedTaskPromoCodeTaskDTO",
]
