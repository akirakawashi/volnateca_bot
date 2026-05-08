from fastapi.responses import PlainTextResponse
from loguru import logger

from application.command.create_vk_post_tasks import (
    CreateVKPostTasksCommand,
    CreateVKPostTasksHandler,
)
from presentation.http.dto.request import VKCallbackSchema
from presentation.http.routers.v1.routers.vk_callbacks.responses import vk_ok_response


async def handle_wall_post_new_callback(
    data: VKCallbackSchema,
    interactor: CreateVKPostTasksHandler,
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
        command_data=CreateVKPostTasksCommand(
            event_id=data.event_id,
            group_id=data.group_id,
            post=post,
            text=data.get_wall_post_text(),
        ),
    )
    logger.info(
        "TEMP VK wall_post_new callback processed: "
        "event_id={}, event_type={}, status={}, external_id={}, "
        "repost_tasks_id={}, like_tasks_id={}, "
        "repost_points={}, like_points={}, week_number={}, reason={}",
        data.event_id,
        data.type,
        result.status,
        result.external_id,
        result.repost_tasks_id,
        result.like_tasks_id,
        result.repost_points,
        result.like_points,
        result.week_number,
        result.reason,
    )
    return vk_ok_response()
