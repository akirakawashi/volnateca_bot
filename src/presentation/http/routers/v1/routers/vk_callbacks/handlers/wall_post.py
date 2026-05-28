from fastapi.responses import PlainTextResponse

from application.command.ensure_vk_poll_task import (
    EnsureVKPollTaskCommand,
    EnsureVKPollTaskHandler,
)
from presentation.http.routers.v1.routers.vk_callbacks.protocol.payload import VKCallbackPayload
from presentation.http.routers.v1.routers.vk_callbacks.protocol.responses import vk_ok_response


async def handle_wall_post_callback(
    data: VKCallbackPayload,
    interactor: EnsureVKPollTaskHandler,
) -> PlainTextResponse:
    """Создаёт бессрочное poll-задание по посту с опросом и #volnateca."""

    if not data.is_wall_post_event():
        return vk_ok_response()

    poll = data.get_wall_post_poll()
    if poll is None:
        return vk_ok_response()

    await interactor(
        command_data=EnsureVKPollTaskCommand(
            post_text=data.get_wall_post_text(),
            poll=poll,
            poll_question=data.get_wall_post_poll_question(),
        ),
    )
    return vk_ok_response()
