from dataclasses import dataclass

from domain.enums.task import TaskPromoCodeWaitStatus


@dataclass(slots=True, frozen=True, kw_only=True)
class TaskPromoCodeRecord:
    task_promo_codes_id: int
    tasks_id: int
    promo_code: str


@dataclass(slots=True, frozen=True, kw_only=True)
class TaskPromoCodeWaitRecord:
    task_promo_code_waits_id: int
    users_id: int
    tasks_id: int
    wait_status: TaskPromoCodeWaitStatus


def normalize_task_promo_code(value: str) -> str:
    """Нормализует ввод пользователя и значения, загружаемые через админский API."""

    return "".join(value.split()).upper()
