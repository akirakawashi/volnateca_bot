from fastapi.responses import PlainTextResponse
from loguru import logger

from application.command.complete_vk_subscription_task import (
    CompleteVKSubscriptionTaskCommand,
    CompleteVKSubscriptionTaskHandler,
)
from presentation.http.dto.request import VKCallbackSchema
from presentation.http.routers.v1.routers.vk_callbacks.responses import vk_ok_response


async def handle_subscription_callback(
    data: VKCallbackSchema,
    interactor: CompleteVKSubscriptionTaskHandler,
) -> PlainTextResponse:
    vk_user_id = data.get_vk_user_id()
    if vk_user_id is None:
        logger.warning(
            "VK subscription callback without user id: event_id={}, event_type={}",
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
        "VK subscription callback processed: "
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
    return vk_ok_response()
