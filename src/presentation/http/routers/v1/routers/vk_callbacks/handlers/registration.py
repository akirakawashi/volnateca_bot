from fastapi.responses import PlainTextResponse

from application.command.get_vk_user_tasks import GetVKUserTasksCommand, GetVKUserTasksHandler
from application.command.register_vk_user import REGISTRATION_BONUS_POINTS
from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionCommand,
    RegisterVKUserAndCheckSubscriptionDTO,
    RegisterVKUserAndCheckSubscriptionHandler,
)
from application.common.dto.task import TaskCompletionResultStatus
from application.common.dto.user_message import UserMessageIntent
from application.interface.clients import IVKMessageClient
from application.interface.services import IUserMessageIntentClassifier
from presentation.http.routers.v1.routers.vk_callbacks.messages import (
    VKMessageText,
    build_balance_message,
    build_free_text_fallback_message,
    build_help_message,
    build_registration_welcome_message,
    build_subscription_reward_message,
    build_tasks_message,
)
from presentation.http.routers.v1.routers.vk_callbacks.message_sender import send_vk_user_message
from presentation.http.routers.v1.routers.vk_callbacks.payload import VKCallbackPayload
from presentation.http.routers.v1.routers.vk_callbacks.responses import vk_ok_response


async def handle_registration_callback(
    data: VKCallbackPayload,
    interactor: RegisterVKUserAndCheckSubscriptionHandler,
    get_vk_user_tasks_interactor: GetVKUserTasksHandler,
    message_client: IVKMessageClient,
    intent_classifier: IUserMessageIntentClassifier,
) -> PlainTextResponse:
    vk_user_id = data.get_vk_user_id()
    if vk_user_id is None:
        return vk_ok_response()

    result = await interactor(
        command_data=RegisterVKUserAndCheckSubscriptionCommand(
            event_id=data.event_id,
            vk_user_id=vk_user_id,
            first_name=data.get_first_name(),
            last_name=data.get_last_name(),
        ),
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
            get_vk_user_tasks_interactor=get_vk_user_tasks_interactor,
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
    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=message,
        message_client=message_client,
        log_message="Приветственное сообщение VK после регистрации",
    )


async def _send_subscription_reward_message_after_registration(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    message_client: IVKMessageClient,
) -> None:
    subscription = result.subscription
    if subscription is None or subscription.status != TaskCompletionResultStatus.COMPLETED:
        return
    if subscription.balance_points is None:
        return

    message = build_subscription_reward_message(
        points_awarded=subscription.points_awarded,
        balance_points=subscription.balance_points,
    )
    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=message,
        message_client=message_client,
        log_message="Сообщение о награде за подписку VK после регистрации",
    )


async def _handle_registered_user_message(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    message_client: IVKMessageClient,
    intent_classifier: IUserMessageIntentClassifier,
    get_vk_user_tasks_interactor: GetVKUserTasksHandler,
) -> None:
    message_text = data.get_message_text()
    classified = await intent_classifier.classify(text=message_text)
    if classified.intent == UserMessageIntent.TASKS:
        tasks_result = await get_vk_user_tasks_interactor(
            command_data=GetVKUserTasksCommand(vk_user_id=result.registration.vk_user_id),
        )
        response = build_tasks_message(tasks=tasks_result.tasks)
    else:
        response = _build_registered_user_response(
            intent=classified.intent,
            balance_points=result.registration.balance_points,
        )
    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=response,
        message_client=message_client,
        log_message="Ответ VK зарегистрированному пользователю",
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
