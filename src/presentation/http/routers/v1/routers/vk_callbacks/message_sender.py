from loguru import logger

from application.interface.clients import IVKMessageClient
from presentation.http.routers.v1.routers.vk_callbacks.keyboards import build_main_menu_keyboard
from presentation.http.routers.v1.routers.vk_callbacks.messages import VKMessageText
from presentation.http.routers.v1.routers.vk_callbacks.payload import VKCallbackPayload


async def send_vk_user_message(
    *,
    data: VKCallbackPayload,
    vk_user_id: int,
    users_id: int,
    message: VKMessageText,
    message_client: IVKMessageClient,
    log_message: str,
) -> None:
    try:
        await message_client.send_message(
            vk_user_id=vk_user_id,
            message=message.text,
            keyboard=build_main_menu_keyboard(),
        )
    except Exception:
        logger.exception(
            "{} не отправлено из-за ошибки: event_id={}, vk_user_id={}, users_id={}",
            log_message,
            data.event_id,
            vk_user_id,
            users_id,
        )
        return


__all__ = ["send_vk_user_message"]
