from fastapi.responses import PlainTextResponse
from loguru import logger

from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionCommand,
    RegisterVKUserAndCheckSubscriptionHandler,
)
from presentation.http.routers.v1.routers.vk_callbacks.payload import VKCallbackPayload
from presentation.http.routers.v1.routers.vk_callbacks.responses import vk_ok_response


async def handle_registration_callback(
    data: VKCallbackPayload,
    interactor: RegisterVKUserAndCheckSubscriptionHandler,
) -> PlainTextResponse:
    vk_user_id = data.get_vk_user_id()
    if vk_user_id is None:
        logger.warning(
            "TEMP VK registration callback without user id: event_id={}, event_type={}",
            data.event_id,
            data.type,
        )
        return vk_ok_response()

    result = await interactor(
        command_data=RegisterVKUserAndCheckSubscriptionCommand(
            event_id=data.event_id,
            vk_user_id=vk_user_id,
            first_name=data.get_first_name(),
            last_name=data.get_last_name(),
        ),
    )
    logger.info(
        "TEMP VK registration callback processed: "
        "event_id={}, event_type={}, vk_user_id={}, users_id={}, created={}, screen_name={}",
        data.event_id,
        data.type,
        result.registration.vk_user_id,
        result.registration.users_id,
        result.registration.created,
        result.registration.vk_screen_name,
    )
    logger.info(
        "VK subscription check after registration processed: "
        "event_id={}, event_type={}, vk_user_id={}, status={}, users_id={}, tasks_id={}, "
        "task_completions_id={}, transactions_id={}, points_awarded={}, balance_points={}, rejected_reason={}",
        data.event_id,
        data.type,
        result.subscription.vk_user_id,
        result.subscription.status,
        result.subscription.users_id,
        result.subscription.tasks_id,
        result.subscription.task_completions_id,
        result.subscription.transactions_id,
        result.subscription.points_awarded,
        result.subscription.balance_points,
        result.subscription.rejected_reason,
    )
    return vk_ok_response()
