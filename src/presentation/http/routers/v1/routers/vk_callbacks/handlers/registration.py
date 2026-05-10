from fastapi.responses import PlainTextResponse
from loguru import logger

from application.command.register_vk_user import REGISTRATION_BONUS_POINTS
from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionCommand,
    RegisterVKUserAndCheckSubscriptionDTO,
    RegisterVKUserAndCheckSubscriptionHandler,
)
from application.interface.clients import IVKMessageClient
from presentation.http.routers.v1.routers.vk_callbacks.messages import build_registration_welcome_message
from presentation.http.routers.v1.routers.vk_callbacks.payload import VKCallbackPayload
from presentation.http.routers.v1.routers.vk_callbacks.responses import vk_ok_response


async def handle_registration_callback(
    data: VKCallbackPayload,
    interactor: RegisterVKUserAndCheckSubscriptionHandler,
    message_client: IVKMessageClient,
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
    if result.subscription is None:
        logger.info(
            "VK subscription check after registration skipped (user already registered): "
            "event_id={}, event_type={}, vk_user_id={}, users_id={}",
            data.event_id,
            data.type,
            result.registration.vk_user_id,
            result.registration.users_id,
        )
    else:
        logger.info(
            "VK subscription check after registration processed: "
            "event_id={}, event_type={}, vk_user_id={}, status={}, users_id={}, tasks_id={}, "
            "task_completions_id={}, transactions_id={}, "
            "points_awarded={}, balance_points={}, rejected_reason={}",
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
    if result.registration.created:
        await _send_registration_welcome_message(
            data=data,
            result=result,
            message_client=message_client,
        )
    return vk_ok_response()


async def _send_registration_welcome_message(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    message_client: IVKMessageClient,
) -> None:
    message = build_registration_welcome_message(
        first_name=data.get_first_name(),
        balance_points=_get_actual_balance_points(result=result),
        bonus_points=REGISTRATION_BONUS_POINTS,
    )
    try:
        sent = await message_client.send_message(
            vk_user_id=result.registration.vk_user_id,
            message=message.text,
        )
    except Exception:
        logger.exception(
            "VK registration welcome message failed: event_id={}, vk_user_id={}, users_id={}",
            data.event_id,
            result.registration.vk_user_id,
            result.registration.users_id,
        )
        return

    if not sent:
        logger.warning(
            "VK registration welcome message was not sent: event_id={}, vk_user_id={}, users_id={}",
            data.event_id,
            result.registration.vk_user_id,
            result.registration.users_id,
        )


def _get_actual_balance_points(result: RegisterVKUserAndCheckSubscriptionDTO) -> int:
    if result.subscription is not None and result.subscription.balance_points is not None:
        return result.subscription.balance_points
    return result.registration.balance_points
