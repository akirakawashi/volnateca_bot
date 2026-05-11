from datetime import datetime

from domain.enums.task import TaskRepeatPolicy


def build_task_completion_key(
    *,
    repeat_policy: TaskRepeatPolicy,
    week_number: int | None,
    checked_at: datetime,
) -> str:
    """Возвращает идемпотентный ключ выполнения задания для текущего периода.

    ONCE всегда даёт один ключ, DAILY привязан к календарной дате, WEEKLY
    использует номер недели проекта, а если его нет — ISO-неделю checked_at.
    """

    if repeat_policy == TaskRepeatPolicy.ONCE:
        return "once"
    if repeat_policy == TaskRepeatPolicy.DAILY:
        return checked_at.date().isoformat()
    if repeat_policy == TaskRepeatPolicy.WEEKLY:
        if week_number is not None:
            return f"week_{week_number:02d}"

        # Недельные задания без номера недели проекта используют календарную ISO-неделю.
        iso_calendar = checked_at.isocalendar()
        return f"{iso_calendar.year}-W{iso_calendar.week:02d}"

    raise ValueError(f"Неподдерживаемая политика повторения задания: {repeat_policy}")
