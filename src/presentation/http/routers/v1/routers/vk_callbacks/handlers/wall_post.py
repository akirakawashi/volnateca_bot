from fastapi.responses import PlainTextResponse

from application.command.create_vk_post_tasks import (
    CreateVKPostTasksCommand,
    CreateVKPostTasksHandler,
)
from presentation.http.routers.v1.routers.vk_callbacks.payload import VKCallbackPayload
from presentation.http.routers.v1.routers.vk_callbacks.responses import vk_ok_response


async def handle_wall_post_new_callback(
    data: VKCallbackPayload,
    interactor: CreateVKPostTasksHandler,
) -> PlainTextResponse:
    """Запускает создание заданий из нового поста группы и всегда отвечает VK ok."""

    post = data.get_wall_post()
    if post is None or data.group_id is None:
        return vk_ok_response()

    await interactor(
        command_data=CreateVKPostTasksCommand(
            event_id=data.event_id,
            group_id=data.group_id,
            post=post,
            text=data.get_wall_post_text(),
        ),
    )
    return vk_ok_response()
