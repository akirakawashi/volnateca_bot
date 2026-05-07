from fastapi.responses import PlainTextResponse

VK_CALLBACK_OK_RESPONSE = "ok"


def vk_ok_response() -> PlainTextResponse:
    return PlainTextResponse(VK_CALLBACK_OK_RESPONSE)
