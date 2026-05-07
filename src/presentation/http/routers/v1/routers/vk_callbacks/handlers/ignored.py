from fastapi.responses import PlainTextResponse
from loguru import logger

from presentation.http.dto.request import VKCallbackSchema
from presentation.http.routers.v1.routers.vk_callbacks.responses import vk_ok_response


def handle_ignored_callback(data: VKCallbackSchema) -> PlainTextResponse:
    logger.info(
        "TEMP VK callback ignored: event_id={}, event_type={}",
        data.event_id,
        data.type,
    )
    return vk_ok_response()
