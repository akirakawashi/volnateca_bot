from application.common.dto.task import TaskPaginationDTO, VKUserAvailableTaskDTO
from presentation.http.routers.v1.routers.vk_callbacks.outbound.keyboards._buttons import (
    VKKeyboard,
    VKTemplate,
    _payload_button,
    _truncate_carousel_text,
)
from presentation.http.routers.v1.routers.vk_callbacks.outbound.keyboards.registration import (
    _build_main_menu_rows,
)
from settings.vk.task_images import TaskTypeImagesSettings
from utils.vk_attachments import to_vk_carousel_photo_id


def build_tasks_navigation_keyboard(pagination: TaskPaginationDTO | None = None) -> VKKeyboard:
    buttons: list[list[dict[str, object]]] = []

    navigation_row = _build_tasks_navigation_row(pagination)
    if navigation_row:
        buttons.append(navigation_row)

    buttons.extend(_build_main_menu_rows())
    return {"one_time": False, "buttons": buttons}


def build_task_info_keyboard(pagination: TaskPaginationDTO | None = None) -> VKKeyboard:
    page = 1 if pagination is None else pagination.page
    buttons: list[list[dict[str, object]]] = [
        [
            _payload_button(
                label="К списку заданий",
                color="primary",
                payload={"action": "tasks_page", "page": page},
            ),
        ],
    ]

    navigation_row = _build_tasks_navigation_row(pagination)
    if navigation_row:
        buttons.append(navigation_row)

    buttons.extend(_build_main_menu_rows())
    return {"one_time": False, "buttons": buttons}


def _build_tasks_navigation_row(pagination: TaskPaginationDTO | None) -> list[dict[str, object]]:
    if pagination is None:
        return []

    buttons: list[dict[str, object]] = []
    if pagination.has_previous:
        buttons.append(
            _payload_button(
                label="← Назад",
                color="secondary",
                payload={"action": "tasks_page", "page": pagination.page - 1},
            ),
        )
    if pagination.has_next:
        buttons.append(
            _payload_button(
                label="Вперёд →",
                color="secondary",
                payload={"action": "tasks_page", "page": pagination.page + 1},
            ),
        )
    return buttons


def build_tasks_carousel_template(
    tasks: tuple[VKUserAvailableTaskDTO, ...],
    task_images_settings: TaskTypeImagesSettings,
    *,
    page: int = 1,
) -> VKTemplate | None:
    if not tasks:
        return None

    elements: list[dict[str, object]] = []
    for task in tasks:
        photo_id = to_vk_carousel_photo_id(task_images_settings.get_image(task.task_type))
        if photo_id is None:
            return None

        button_payload: dict[str, object] = {
            "action": "task_info",
            "tasks_id": task.tasks_id,
            "page": page,
        }
        elements.append(
            {
                "title": _truncate_carousel_text(task.task_name, max_length=80),
                "description": _truncate_carousel_text(f"+{task.points} ✦", max_length=80),
                "photo_id": photo_id,
                "action": {"type": "open_photo"},
                "buttons": [
                    _payload_button(
                        label="Подробнее",
                        color="primary",
                        payload=button_payload,
                    ),
                ],
            },
        )

    return {
        "type": "carousel",
        "elements": elements,
    }
