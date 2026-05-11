from fastapi.responses import PlainTextResponse
from loguru import logger

from application.command.complete_vk_like_task import (
    CompleteVKLikeTaskCommand,
    CompleteVKLikeTaskHandler,
)
from application.common.dto.task import TaskCompletionResult, TaskCompletionResultStatus
from application.interface.clients import IVKMessageClient
from presentation.http.routers.v1.routers.vk_callbacks.messages import (
    build_like_reward_message,
)
from presentation.http.routers.v1.routers.vk_callbacks.message_sender import send_vk_user_message
from presentation.http.routers.v1.routers.vk_callbacks.payload import VKCallbackPayload
from presentation.http.routers.v1.routers.vk_callbacks.responses import vk_ok_response


async def handle_like_callback(
    data: VKCallbackPayload,
    interactor_complete: CompleteVKLikeTaskHandler,
    message_client: IVKMessageClient,
) -> PlainTextResponse:
    if data.type != "like_add":
        logger.info(
            "ВРЕМЕННО Событие лайка VK проигнорировано, событие не like_add: event_type={}, liker_id={}",
            data.type,
            data.get_like_user_id(),
        )
        return vk_ok_response()

    liker_id = data.get_like_user_id()
    if liker_id is None:
        logger.warning(
            "ВРЕМЕННО Событие VK like_add без liker_id: event_id={}",
            data.event_id,
        )
        return vk_ok_response()

    liked_post_external_ids = data.get_liked_post_external_ids()
    result = await interactor_complete(
        command_data=CompleteVKLikeTaskCommand(
            event_id=data.event_id,
            vk_user_id=liker_id,
            liked_post_external_ids=liked_post_external_ids,
        ),
    )
    logger.info(
        "ВРЕМЕННО Событие VK like_add обработано: "
        "event_id={}, liker_id={}, status={}, users_id={}, tasks_id={}, "
        "task_completions_id={}, transactions_id={}, points_awarded={}, balance_points={}",
        data.event_id,
        liker_id,
        result.status,
        result.users_id,
        result.tasks_id,
        result.task_completions_id,
        result.transactions_id,
        result.points_awarded,
        result.balance_points,
    )
    if result.status == TaskCompletionResultStatus.COMPLETED:
        await _send_like_reward_message(
            data=data,
            result=result,
            message_client=message_client,
        )
    return vk_ok_response()


async def _send_like_reward_message(
    *,
    data: VKCallbackPayload,
    result: TaskCompletionResult,
    message_client: IVKMessageClient,
) -> None:
    if result.users_id is None or result.balance_points is None:
        logger.warning(
            "Сообщение о награде за лайк VK пропущено без пользователя или баланса: "
            "event_id={}, vk_user_id={}, users_id={}",
            data.event_id,
            result.vk_user_id,
            result.users_id,
        )
        return

    message = build_like_reward_message(
        points_awarded=result.points_awarded,
        balance_points=result.balance_points,
    )
    await send_vk_user_message(
        data=data,
        vk_user_id=result.vk_user_id,
        users_id=result.users_id,
        message=message,
        message_client=message_client,
        log_message="Сообщение о награде за лайк VK",
    )
