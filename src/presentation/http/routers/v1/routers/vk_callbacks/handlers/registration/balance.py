"""Обработчик показа баланса баллов зарегистрированного пользователя."""

from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionDTO,
)
from application.interface.clients import IVKMessageClient
from presentation.http.routers.v1.routers.vk_callbacks.message_sender import send_vk_user_message
from presentation.http.routers.v1.routers.vk_callbacks.messages import build_balance_message
from presentation.http.routers.v1.routers.vk_callbacks.payload import VKCallbackPayload


async def handle_balance(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    message_client: IVKMessageClient,
) -> None:
    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=build_balance_message(balance_points=result.registration.balance_points),
        message_client=message_client,
        log_message="Баланс VK",
    )
