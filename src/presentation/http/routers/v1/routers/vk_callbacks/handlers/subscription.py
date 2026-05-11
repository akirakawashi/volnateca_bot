from fastapi.responses import PlainTextResponse
from loguru import logger

from application.command.complete_vk_subscription_task import (
    CompleteVKSubscriptionTaskCommand,
    CompleteVKSubscriptionTaskHandler,
)
from application.common.dto.task import TaskCompletionResult, TaskCompletionResultStatus
from application.interface.clients import IVKMessageClient
from presentation.http.routers.v1.routers.vk_callbacks.messages import (
    build_subscription_reward_message,
)
from presentation.http.routers.v1.routers.vk_callbacks.message_sender import send_vk_user_message
from presentation.http.routers.v1.routers.vk_callbacks.payload import VKCallbackPayload
from presentation.http.routers.v1.routers.vk_callbacks.responses import vk_ok_response


async def handle_subscription_callback(
    data: VKCallbackPayload,
    interactor: CompleteVKSubscriptionTaskHandler,
    message_client: IVKMessageClient,
) -> PlainTextResponse:
    vk_user_id = data.get_vk_user_id()
    if vk_user_id is None:
        logger.warning(
            "Событие подписки VK без ID пользователя: event_id={}, event_type={}",
            data.event_id,
            data.type,
        )
        return vk_ok_response()

    result = await interactor(
        command_data=CompleteVKSubscriptionTaskCommand(
            event_id=data.event_id,
            vk_user_id=vk_user_id,
        ),
    )
    logger.info(
        "Событие подписки VK обработано: "
        "event_id={}, event_type={}, vk_user_id={}, status={}, users_id={}, tasks_id={}, "
        "task_completions_id={}, transactions_id={}, points_awarded={}, balance_points={}, rejected_reason={}",
        data.event_id,
        data.type,
        result.vk_user_id,
        result.status,
        result.users_id,
        result.tasks_id,
        result.task_completions_id,
        result.transactions_id,
        result.points_awarded,
        result.balance_points,
        result.rejected_reason,
    )
    if result.status == TaskCompletionResultStatus.COMPLETED:
        await _send_subscription_reward_message(
            data=data,
            result=result,
            message_client=message_client,
        )
    return vk_ok_response()


async def _send_subscription_reward_message(
    *,
    data: VKCallbackPayload,
    result: TaskCompletionResult,
    message_client: IVKMessageClient,
) -> None:
    if result.users_id is None or result.balance_points is None:
        logger.warning(
            "Сообщение о награде за подписку VK пропущено без пользователя или баланса: "
            "event_id={}, vk_user_id={}, users_id={}",
            data.event_id,
            result.vk_user_id,
            result.users_id,
        )
        return

    message = build_subscription_reward_message(
        points_awarded=result.points_awarded,
        balance_points=result.balance_points,
    )
    await send_vk_user_message(
        data=data,
        vk_user_id=result.vk_user_id,
        users_id=result.users_id,
        message=message,
        message_client=message_client,
        log_message="Сообщение о награде за подписку VK",
    )
