from fastapi.responses import PlainTextResponse
from loguru import logger

from application.command.complete_vk_like_task import (
    CompleteVKLikeTaskCommand,
    CompleteVKLikeTaskHandler,
)
from presentation.http.dto.request import VKCallbackSchema
from presentation.http.routers.v1.routers.vk_callbacks.responses import vk_ok_response


async def handle_like_callback(
    data: VKCallbackSchema,
    interactor_complete: CompleteVKLikeTaskHandler,
) -> PlainTextResponse:
    if data.type != "like_add":
        logger.info(
            "TEMP VK like callback ignored (not like_add): event_type={}, liker_id={}",
            data.type,
            data.get_like_user_id(),
        )
        return vk_ok_response()

    liker_id = data.get_like_user_id()
    if liker_id is None:
        logger.warning(
            "TEMP VK like_add callback without liker_id: event_id={}",
            data.event_id,
        )
        return vk_ok_response()

    liked_post_external_ids = data.get_liked_post_external_ids()
    result = await interactor_complete(
        command_data=CompleteVKLikeTaskCommand(
            event_id=data.event_id,
            vk_user_id=liker_id,
            liked_post_external_ids=liked_post_external_ids,
        ),
    )
    logger.info(
        "TEMP VK like_add callback processed: "
        "event_id={}, liker_id={}, status={}, users_id={}, tasks_id={}, "
        "task_completions_id={}, transactions_id={}, points_awarded={}, balance_points={}",
        data.event_id,
        liker_id,
        result.status,
        result.users_id,
        result.tasks_id,
        result.task_completions_id,
        result.transactions_id,
        result.points_awarded,
        result.balance_points,
    )
    return vk_ok_response()
