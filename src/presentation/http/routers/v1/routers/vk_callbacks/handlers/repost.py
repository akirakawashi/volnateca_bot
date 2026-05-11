from fastapi.responses import PlainTextResponse

from application.command.complete_vk_repost_task import (
    CompleteVKRepostTaskCommand,
    CompleteVKRepostTaskHandler,
)
from presentation.http.routers.v1.routers.vk_callbacks.payload import VKCallbackPayload
from presentation.http.routers.v1.routers.vk_callbacks.responses import vk_ok_response


async def handle_repost_callback(
    data: VKCallbackPayload,
    interactor: CompleteVKRepostTaskHandler,
) -> PlainTextResponse:
    vk_user_id = data.get_repost_user_id()
    if vk_user_id is None:
        return vk_ok_response()

    target_post_external_ids = data.get_reposted_wall_post_external_ids()
    if not target_post_external_ids:
        return vk_ok_response()

    await interactor(
        command_data=CompleteVKRepostTaskCommand(
            event_id=data.event_id,
            vk_user_id=vk_user_id,
            repost_external_id=data.get_repost_external_id(),
            target_post_external_ids=target_post_external_ids,
        ),
    )
    return vk_ok_response()
