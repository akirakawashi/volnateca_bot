from dataclasses import dataclass
from datetime import datetime

from domain.enums.task import TaskPromoCodeStatus, TaskPromoCodeWaitStatus


@dataclass(slots=True, frozen=True, kw_only=True)
class TaskPromoCodeRecord:
    task_promo_codes_id: int
    tasks_id: int
    promo_code: str
    promo_code_status: TaskPromoCodeStatus
    users_id: int | None
    activated_at: datetime | None


@dataclass(slots=True, frozen=True, kw_only=True)
class TaskPromoCodeWaitRecord:
    task_promo_code_waits_id: int
    users_id: int
    tasks_id: int
    wait_status: TaskPromoCodeWaitStatus


@dataclass(slots=True, frozen=True, kw_only=True)
class TaskPromoCodeStatsDTO:
    tasks_id: int
    total_count: int
    available_count: int
    used_count: int


def normalize_task_promo_code(value: str) -> str:
    """Нормализует ввод пользователя и значения, загружаемые через админский API."""

    return "".join(value.split()).upper()
