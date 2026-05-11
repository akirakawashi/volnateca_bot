from fastapi.responses import PlainTextResponse
from loguru import logger

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
        logger.warning(
            "ВРЕМЕННО Событие репоста VK без ID пользователя: event_id={}, event_type={}",
            data.event_id,
            data.type,
        )
        return vk_ok_response()

    target_post_external_ids = data.get_reposted_wall_post_external_ids()
    if not target_post_external_ids:
        logger.warning(
            "ВРЕМЕННО Событие репоста VK без целевого поста в copy_history: "
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
        "ВРЕМЕННО Событие репоста VK обработано: "
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
