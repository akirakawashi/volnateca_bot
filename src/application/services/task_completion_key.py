from datetime import datetime

from domain.enums.task import TaskRepeatPolicy


def build_task_completion_key(
    *,
    repeat_policy: TaskRepeatPolicy,
    week_number: int | None,
    checked_at: datetime,
) -> str:
    if repeat_policy == TaskRepeatPolicy.ONCE:
        return "once"
    if repeat_policy == TaskRepeatPolicy.DAILY:
        return checked_at.date().isoformat()
    if week_number is not None:
        return f"week_{week_number:02d}"

    iso_calendar = checked_at.isocalendar()
    return f"{iso_calendar.year}-W{iso_calendar.week:02d}"
