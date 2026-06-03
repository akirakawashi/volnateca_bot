from application.common.dto.task import TaskPaginationDTO, VKUserAvailableTaskDTO
from domain.project_rules import MENYAYKA_SALE_URL
from presentation.http.routers.v1.routers.vk_callbacks.outbound.messages.template import (
    VKMessageText,
    build_template_message,
)


def build_task_accrual_message(
    *,
    task_name: str,
    points_awarded: int,
    balance_points: int | None,
) -> VKMessageText:
    balance_line = f"\n\n💫 Баланс: {balance_points} ✦" if balance_points is not None else ""
    return build_template_message(
        "task_accrual",
        task_name=task_name,
        points_awarded=points_awarded,
        balance_line=balance_line,
    )


def build_tasks_message(
    *,
    tasks: tuple[VKUserAvailableTaskDTO, ...],
    pagination: TaskPaginationDTO | None = None,
) -> VKMessageText:
    if not tasks:
        return build_template_message("tasks_empty")

    start_index = 0 if pagination is None else (pagination.page - 1) * pagination.page_size
    blocks: list[str] = []
    for index, task in enumerate(tasks, start=1):
        lines = [
            f"{start_index + index}. {task.task_name}",
            f"+{task.points} ✦",
        ]
        if task.action_url is not None:
            lines.append(task.action_url)
        blocks.append("\n".join(lines))

    tasks_block = "\n\n".join(blocks)
    if pagination is not None:
        tasks_block = f"Страница {pagination.page} из {pagination.total_pages}\n\n{tasks_block}"

    return build_template_message("tasks_list", tasks_block=tasks_block)


def build_tasks_navigation_message(*, pagination: TaskPaginationDTO | None = None) -> VKMessageText:
    return build_template_message(
        "tasks_navigation",
        page=1 if pagination is None else pagination.page,
        total_pages=1 if pagination is None else pagination.total_pages,
    )


def build_tasks_carousel_message(
    *,
    tasks: tuple[VKUserAvailableTaskDTO, ...],
    pagination: TaskPaginationDTO | None = None,
) -> VKMessageText:
    return build_template_message(
        "tasks_carousel",
        available_count=len(tasks) if pagination is None else pagination.total_items,
        page=1 if pagination is None else pagination.page,
        total_pages=1 if pagination is None else pagination.total_pages,
    )


def build_task_info_message(*, task: VKUserAvailableTaskDTO) -> VKMessageText:
    action_url_block = f"\n\n{task.action_url}" if task.action_url is not None else ""
    return build_template_message(
        "task_info",
        task_name=task.task_name,
        points=task.points,
        action_url_block=action_url_block,
    )


def build_custom_promo_task_start_message(
    *,
    task_name: str,
    points: int,
) -> VKMessageText:
    return build_template_message(
        "custom_promo_task_start",
        task_name=task_name,
        points=points,
        menyayka_url=MENYAYKA_SALE_URL,
    )


def build_custom_promo_invalid_code_message() -> VKMessageText:
    return build_template_message("custom_promo_invalid_code")


def build_custom_promo_already_completed_message() -> VKMessageText:
    return build_template_message("custom_promo_already_completed")


def build_custom_promo_canceled_message() -> VKMessageText:
    return build_template_message("custom_promo_canceled")
