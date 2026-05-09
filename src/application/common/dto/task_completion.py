from dataclasses import dataclass
from datetime import datetime

from domain.enums.task import TaskCompletionStatus


@dataclass(slots=True, frozen=True, kw_only=True)
class TaskCompletionRecord:
    """Запись из таблицы task_completions, возвращаемая ITaskCompletionRepository."""

    task_completions_id: int
    users_id: int
    tasks_id: int
    completion_key: str
    transactions_id: int | None
    task_completion_status: TaskCompletionStatus
    points_awarded: int
    external_event_id: str | None
    evidence_external_id: str | None
    rejected_reason: str | None
    checked_at: datetime | None
