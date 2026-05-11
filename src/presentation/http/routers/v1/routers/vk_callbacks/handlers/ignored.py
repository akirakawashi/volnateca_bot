from fastapi.responses import PlainTextResponse

from presentation.http.routers.v1.routers.vk_callbacks.payload import VKCallbackPayload
from presentation.http.routers.v1.routers.vk_callbacks.responses import vk_ok_response


def handle_ignored_callback(data: VKCallbackPayload) -> PlainTextResponse:
    return vk_ok_response()
