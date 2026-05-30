from dataclasses import dataclass
from datetime import datetime

from domain.enums.task import TaskRepeatPolicy


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateTaskPromoCodeTaskCommand:
    code: str
    task_name: str
    description: str | None
    points: int
    week_number: int | None
    starts_at: datetime | None
    ends_at: datetime | None
    repeat_policy: TaskRepeatPolicy
    promo_codes: tuple[str, ...]


@dataclass(slots=True, frozen=True, kw_only=True)
class CreatedTaskPromoCodeTaskDTO:
    tasks_id: int
    code: str
    task_name: str
    promo_codes_total: int


__all__ = [
    "CreateTaskPromoCodeTaskCommand",
    "CreatedTaskPromoCodeTaskDTO",
]
