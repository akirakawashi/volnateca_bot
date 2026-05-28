"""Обработчики списка заданий, карточки задания и общая отрисовка каталога заданий."""

from application.command.get_vk_user_tasks import (
    GetVKUserTasksCommand,
    GetVKUserTasksDTO,
    GetVKUserTasksHandler,
)
from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionDTO,
)
from application.common.dto.task import VKUserAvailableTaskDTO
from application.interface.clients import IVKMessageClient
from presentation.http.routers.v1.routers.vk_callbacks.keyboards import (
    build_quiz_offer_keyboard,
    build_task_info_keyboard,
    build_tasks_carousel_template,
    build_tasks_navigation_keyboard,
)
from presentation.http.routers.v1.routers.vk_callbacks.message_sender import send_vk_user_message
from presentation.http.routers.v1.routers.vk_callbacks.messages import (
    build_quiz_offer_message,
    build_task_info_message,
    build_tasks_carousel_message,
    build_tasks_message,
    build_tasks_navigation_message,
)
from presentation.http.routers.v1.routers.vk_callbacks.payload import VKCallbackPayload
from settings.vk.task_images import TaskTypeImagesSettings


async def handle_tasks(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    page: int,
    include_quiz_offer: bool,
    message_client: IVKMessageClient,
    get_vk_user_tasks_interactor: GetVKUserTasksHandler,
    task_images_settings: TaskTypeImagesSettings,
) -> None:
    tasks_result = await get_vk_user_tasks_interactor(
        command_data=GetVKUserTasksCommand(vk_user_id=result.registration.vk_user_id, page=page),
    )
    if include_quiz_offer and tasks_result.active_quiz is not None:
        quiz = tasks_result.active_quiz
        await send_vk_user_message(
            data=data,
            vk_user_id=result.registration.vk_user_id,
            users_id=result.registration.users_id,
            message=build_quiz_offer_message(
                task_name=quiz.task_name,
                points=quiz.points,
            ),
            keyboard=build_quiz_offer_keyboard(tasks_id=quiz.tasks_id),
            message_client=message_client,
            log_message="Предложение квиза VK",
        )
        return

    await send_tasks_catalog(
        data=data,
        result=result,
        tasks_result=tasks_result,
        message_client=message_client,
        task_images_settings=task_images_settings,
        carousel_log_message="Карусель заданий VK",
        list_log_message="Список заданий VK",
    )


async def handle_task_info(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    tasks_id: int,
    page: int,
    message_client: IVKMessageClient,
    get_vk_user_tasks_interactor: GetVKUserTasksHandler,
) -> None:
    tasks_result = await get_vk_user_tasks_interactor(
        command_data=GetVKUserTasksCommand(vk_user_id=result.registration.vk_user_id, page=page),
    )
    task = next((t for t in tasks_result.tasks if t.tasks_id == tasks_id), None)
    if task is None:
        return
    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=build_task_info_message(task=task),
        keyboard=build_task_info_keyboard(tasks_result.pagination),
        message_client=message_client,
        log_message="Детали задания VK",
    )


async def send_tasks_catalog(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    tasks_result: GetVKUserTasksDTO,
    message_client: IVKMessageClient,
    task_images_settings: TaskTypeImagesSettings,
    carousel_log_message: str,
    list_log_message: str,
) -> None:
    tasks = _get_tasks_page(tasks_result)
    pagination = tasks_result.pagination
    page = 1 if pagination is None else pagination.page
    carousel_template = build_tasks_carousel_template(
        tasks,
        task_images_settings,
        page=page,
    )
    if carousel_template is not None:
        await send_vk_user_message(
            data=data,
            vk_user_id=result.registration.vk_user_id,
            users_id=result.registration.users_id,
            message=build_tasks_navigation_message(pagination=pagination),
            keyboard=build_tasks_navigation_keyboard(pagination),
            message_client=message_client,
            log_message="Навигация заданий VK",
        )

        sent = await send_vk_user_message(
            data=data,
            vk_user_id=result.registration.vk_user_id,
            users_id=result.registration.users_id,
            message=build_tasks_carousel_message(tasks=tasks, pagination=pagination),
            keyboard=None,
            template=carousel_template,
            message_client=message_client,
            log_message=carousel_log_message,
        )
        if sent:
            return

    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=build_tasks_message(tasks=tasks, pagination=pagination),
        keyboard=build_tasks_navigation_keyboard(pagination),
        message_client=message_client,
        log_message=list_log_message,
    )


def _get_tasks_page(tasks_result: GetVKUserTasksDTO) -> tuple[VKUserAvailableTaskDTO, ...]:
    pagination = tasks_result.pagination
    if pagination is None:
        return tasks_result.tasks
    if not tasks_result.page_tasks and tasks_result.tasks:
        start = (pagination.page - 1) * pagination.page_size
        return tasks_result.tasks[start : start + pagination.page_size]
    return tasks_result.page_tasks
