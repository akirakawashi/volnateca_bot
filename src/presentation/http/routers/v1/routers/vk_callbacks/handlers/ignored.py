from fastapi.responses import PlainTextResponse

from presentation.http.routers.v1.routers.vk_callbacks.protocol.payload import VKCallbackPayload
from presentation.http.routers.v1.routers.vk_callbacks.protocol.responses import vk_ok_response


def handle_ignored_callback(data: VKCallbackPayload) -> PlainTextResponse:
    return vk_ok_response()
