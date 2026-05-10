from fastapi.responses import PlainTextResponse
from loguru import logger

from application.command.register_vk_user import REGISTRATION_BONUS_POINTS
from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionCommand,
    RegisterVKUserAndCheckSubscriptionDTO,
    RegisterVKUserAndCheckSubscriptionHandler,
)
from application.common.dto.task import VKSubscriptionTaskCompletionStatus
from application.common.dto.user_message import UserMessageIntent
from application.interface.clients import IVKMessageClient
from application.interface.services import IUserMessageIntentClassifier
from presentation.http.routers.v1.routers.vk_callbacks.keyboards import build_main_menu_keyboard
from presentation.http.routers.v1.routers.vk_callbacks.messages import (
    VKMessageText,
    build_balance_message,
    build_free_text_fallback_message,
    build_help_message,
    build_registration_welcome_message,
    build_subscription_reward_message,
)
from presentation.http.routers.v1.routers.vk_callbacks.payload import VKCallbackPayload
from presentation.http.routers.v1.routers.vk_callbacks.responses import vk_ok_response


async def handle_registration_callback(
    data: VKCallbackPayload,
    interactor: RegisterVKUserAndCheckSubscriptionHandler,
    message_client: IVKMessageClient,
    intent_classifier: IUserMessageIntentClassifier,
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
        await _send_subscription_reward_message_after_registration(
            data=data,
            result=result,
            message_client=message_client,
        )
    elif data.is_message_new():
        await _handle_registered_user_message(
            data=data,
            result=result,
            message_client=message_client,
            intent_classifier=intent_classifier,
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
        balance_points=result.registration.balance_points,
        bonus_points=REGISTRATION_BONUS_POINTS,
    )
    await _send_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=message,
        message_client=message_client,
        log_message="VK registration welcome message",
    )


async def _send_subscription_reward_message_after_registration(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    message_client: IVKMessageClient,
) -> None:
    subscription = result.subscription
    if subscription is None or subscription.status != VKSubscriptionTaskCompletionStatus.COMPLETED:
        return
    if subscription.balance_points is None:
        logger.warning(
            "VK subscription reward message skipped without balance: event_id={}, vk_user_id={}, users_id={}",
            data.event_id,
            result.registration.vk_user_id,
            result.registration.users_id,
        )
        return

    message = build_subscription_reward_message(
        points_awarded=subscription.points_awarded,
        balance_points=subscription.balance_points,
    )
    await _send_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=message,
        message_client=message_client,
        log_message="VK subscription reward message after registration",
    )


async def _handle_registered_user_message(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    message_client: IVKMessageClient,
    intent_classifier: IUserMessageIntentClassifier,
) -> None:
    message_text = data.get_message_text()
    classified = await intent_classifier.classify(text=message_text)
    response = _build_registered_user_response(
        intent=classified.intent,
        balance_points=result.registration.balance_points,
    )
    await _send_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=response,
        message_client=message_client,
        log_message="VK registered user message response",
    )
    logger.info(
        "VK registered user message handled: event_id={}, vk_user_id={}, users_id={}, intent={}, confidence={}",
        data.event_id,
        result.registration.vk_user_id,
        result.registration.users_id,
        classified.intent,
        classified.confidence,
    )


def _build_registered_user_response(
    *,
    intent: UserMessageIntent,
    balance_points: int,
) -> VKMessageText:
    if intent == UserMessageIntent.BALANCE:
        return build_balance_message(balance_points=balance_points)
    if intent == UserMessageIntent.HELP:
        return build_help_message()
    return build_free_text_fallback_message()


async def _send_user_message(
    *,
    data: VKCallbackPayload,
    vk_user_id: int,
    users_id: int,
    message: VKMessageText,
    message_client: IVKMessageClient,
    log_message: str,
) -> None:
    try:
        sent = await message_client.send_message(
            vk_user_id=vk_user_id,
            message=message.text,
            keyboard=build_main_menu_keyboard(),
        )
    except Exception:
        logger.exception(
            "{} failed: event_id={}, vk_user_id={}, users_id={}",
            log_message,
            data.event_id,
            vk_user_id,
            users_id,
        )
        return

    if not sent:
        logger.warning(
            "{} was not sent: event_id={}, vk_user_id={}, users_id={}",
            log_message,
            data.event_id,
            vk_user_id,
            users_id,
        )
