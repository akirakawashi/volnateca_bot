from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True, kw_only=True)
class CreatedTaskPromoCodeTaskDTO:
    tasks_id: int
    code: str
    task_name: str
    promo_code: str


@dataclass(slots=True, frozen=True, kw_only=True)
class TaskPromoCodeTaskAdminDTO:
    tasks_id: int
    code: str
    task_name: str
    description: str | None
    points: int
    week_number: int | None
    starts_at: datetime | None
    ends_at: datetime | None
    promo_code: str
    image_attachment: str | None
    can_edit: bool


__all__ = [
    "CreatedTaskPromoCodeTaskDTO",
    "TaskPromoCodeTaskAdminDTO",
]
