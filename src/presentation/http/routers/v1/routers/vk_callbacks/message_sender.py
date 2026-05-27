from contextlib import contextmanager
from contextvars import ContextVar
from loguru import logger

from application.interface.clients import IVKMessageClient
from application.interface.services import IVKMessageTemplateService
from presentation.http.routers.v1.routers.vk_callbacks.keyboards import (
    VKKeyboard,
    VKTemplate,
    build_main_menu_keyboard,
)
from presentation.http.routers.v1.routers.vk_callbacks.messages import VKMessageText
from presentation.http.routers.v1.routers.vk_callbacks.payload import VKCallbackPayload

_message_template_service_ctx: ContextVar[IVKMessageTemplateService | None] = ContextVar(
    "message_template_service",
    default=None,
)


@contextmanager
def bind_vk_message_template_service(service: IVKMessageTemplateService):
    token = _message_template_service_ctx.set(service)
    try:
        yield
    finally:
        _message_template_service_ctx.reset(token)


async def send_vk_user_message(
    *,
    data: VKCallbackPayload,
    vk_user_id: int,
    users_id: int | None,
    message: VKMessageText,
    message_client: IVKMessageClient,
    log_message: str,
    keyboard: VKKeyboard | None = None,
    attachment: str | None = None,
    template: VKTemplate | None = None,
) -> bool:
    """Отправляет VK-сообщение и логирует сбой, не ломая обработку callback-а."""

    try:
        message_text = await _resolve_message_text(message=message)
        keyboard_to_send = keyboard
        if keyboard_to_send is None and template is None:
            keyboard_to_send = build_main_menu_keyboard()

        sent = await message_client.send_message(
            vk_user_id=vk_user_id,
            message=message_text,
            keyboard=keyboard_to_send,
            attachment=attachment,
            template=template,
        )
        if not sent:
            logger.error(
                "{} не отправлено: VK API не подтвердил отправку, event_id={}, vk_user_id={}, users_id={}",
                log_message,
                data.event_id,
                vk_user_id,
                users_id,
            )
        return sent
    except Exception:
        logger.exception(
            "{} не отправлено из-за ошибки: event_id={}, vk_user_id={}, users_id={}",
            log_message,
            data.event_id,
            vk_user_id,
            users_id,
        )
        return False


async def _resolve_message_text(*, message: VKMessageText) -> str:
    service = _message_template_service_ctx.get()
    if service is None:
        return message.text

    try:
        return await service.render(
            code=message.template_code,
            fallback_text=message.text,
            context=message.template_context,
        )
    except Exception:
        return message.text


__all__ = ["bind_vk_message_template_service", "send_vk_user_message"]
