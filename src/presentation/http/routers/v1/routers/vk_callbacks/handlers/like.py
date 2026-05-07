from fastapi.responses import PlainTextResponse
from loguru import logger

from presentation.http.dto.request import VKCallbackSchema
from presentation.http.routers.v1.routers.vk_callbacks.responses import vk_ok_response


def handle_like_callback(data: VKCallbackSchema) -> PlainTextResponse:
    logger.info(
        "TEMP VK like callback received: event_type={}, liker_id={}",
        data.type,
        data.get_like_user_id(),
    )
    return vk_ok_response()
