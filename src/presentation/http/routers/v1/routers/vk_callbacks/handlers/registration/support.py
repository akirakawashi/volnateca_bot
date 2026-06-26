"""Обработчик технической поддержки."""

from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionDTO,
)
from application.interface.clients import IVKMessageClient
from presentation.http.routers.v1.routers.vk_callbacks.outbound.sender import send_vk_user_message
from presentation.http.routers.v1.routers.vk_callbacks.outbound.messages.template import VKMessageText
from presentation.http.routers.v1.routers.vk_callbacks.protocol.payload import VKCallbackPayload


async def handle_support(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    message_client: IVKMessageClient,
    support_link: str,
) -> None:
    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=VKMessageText(text=support_link),
        message_client=message_client,
        log_message="Техническая поддержка",
    )
