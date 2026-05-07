from fastapi.responses import PlainTextResponse

from settings.vk import VKSettings


def handle_confirmation_callback(vk_settings: VKSettings) -> PlainTextResponse:
    return PlainTextResponse(vk_settings.CONFIRMATION_CODE)
