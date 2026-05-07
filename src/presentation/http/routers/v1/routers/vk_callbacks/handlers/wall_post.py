from fastapi.responses import PlainTextResponse
from loguru import logger

from application.command.create_vk_repost_task_from_wall_post import (
    CreateVKRepostTaskFromWallPostCommand,
    CreateVKRepostTaskFromWallPostHandler,
)
from presentation.http.dto.request import VKCallbackSchema
from presentation.http.routers.v1.routers.vk_callbacks.responses import vk_ok_response


async def handle_wall_post_new_callback(
    data: VKCallbackSchema,
    interactor: CreateVKRepostTaskFromWallPostHandler,
) -> PlainTextResponse:
    post = data.get_wall_post()
    if post is None or data.group_id is None:
        logger.warning(
            "TEMP VK wall_post_new callback without post data: event_id={}, event_type={}, group_id={}",
            data.event_id,
            data.type,
            data.group_id,
        )
        return vk_ok_response()

    result = await interactor(
        command_data=CreateVKRepostTaskFromWallPostCommand(
            event_id=data.event_id,
            group_id=data.group_id,
            post=post,
            text=data.get_wall_post_text(),
        ),
    )
    logger.info(
        "TEMP VK wall_post_new callback processed: "
        "event_id={}, event_type={}, status={}, tasks_id={}, code={}, external_id={}, "
        "points={}, week_number={}, reason={}",
        data.event_id,
        data.type,
        result.status,
        result.tasks_id,
        result.code,
        result.external_id,
        result.points,
        result.week_number,
        result.reason,
    )
    return vk_ok_response()
