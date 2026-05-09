from fastapi.responses import PlainTextResponse
from loguru import logger

from application.command.complete_vk_repost_task import (
    CompleteVKRepostTaskCommand,
    CompleteVKRepostTaskHandler,
)
from presentation.http.dto.request import VKCallbackSchema
from presentation.http.routers.v1.routers.vk_callbacks.responses import vk_ok_response


async def handle_repost_callback(
    data: VKCallbackSchema,
    interactor: CompleteVKRepostTaskHandler,
) -> PlainTextResponse:
    vk_user_id = data.get_repost_user_id()
    if vk_user_id is None:
        logger.warning(
            "TEMP VK repost callback without user id: event_id={}, event_type={}",
            data.event_id,
            data.type,
        )
        return vk_ok_response()

    target_post_external_ids = data.get_reposted_wall_post_external_ids()
    if not target_post_external_ids:
        logger.warning(
            "TEMP VK repost callback without copy_history target: "
            "event_id={}, event_type={}, vk_user_id={}, repost_external_id={}",
            data.event_id,
            data.type,
            vk_user_id,
            data.get_repost_external_id(),
        )
        return vk_ok_response()

    result = await interactor(
        command_data=CompleteVKRepostTaskCommand(
            event_id=data.event_id,
            vk_user_id=vk_user_id,
            repost_external_id=data.get_repost_external_id(),
            target_post_external_ids=target_post_external_ids,
        ),
    )
    logger.info(
        "TEMP VK repost callback processed: "
        "event_id={}, event_type={}, vk_user_id={}, status={}, users_id={}, tasks_id={}, "
        "task_completions_id={}, transactions_id={}, points_awarded={}, balance_points={}",
        data.event_id,
        data.type,
        result.vk_user_id,
        result.status,
        result.users_id,
        result.tasks_id,
        result.task_completions_id,
        result.transactions_id,
        result.points_awarded,
        result.balance_points,
    )
    return vk_ok_response()
