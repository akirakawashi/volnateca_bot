from fastapi.responses import PlainTextResponse

from application.command.complete_vk_like_task import (
    CompleteVKLikeTaskCommand,
    CompleteVKLikeTaskHandler,
)
from application.command.complete_vk_repost_task import (
    CompleteVKRepostTaskCommand,
    CompleteVKRepostTaskHandler,
)
from application.common.dto.task import TaskCompletionResult, TaskCompletionResultStatus
from application.interface.clients import IVKMessageClient
from domain.services.level import get_level_name
from presentation.http.routers.v1.routers.vk_callbacks.handlers.achievement import (
    send_project_completion_reward_if_needed,
    send_week_completion_reward_if_needed,
)
from presentation.http.routers.v1.routers.vk_callbacks.messages import (
    build_level_up_message,
    build_like_reward_message,
    build_repost_reward_message,
)
from presentation.http.routers.v1.routers.vk_callbacks.message_sender import send_vk_user_message
from presentation.http.routers.v1.routers.vk_callbacks.payload import VKCallbackPayload
from presentation.http.routers.v1.routers.vk_callbacks.responses import vk_ok_response


async def handle_repost_callback(
    data: VKCallbackPayload,
    interactor: CompleteVKRepostTaskHandler,
    interactor_like: CompleteVKLikeTaskHandler,
    message_client: IVKMessageClient,
) -> PlainTextResponse:
    """Засчитывает репост, если callback содержит автора и исходный пост задания.

    При репосте VK автоматически ставит лайк на исходный пост, но не присылает
    отдельный callback like_add — поэтому лайк засчитывается здесь явно.
    """

    vk_user_id = data.get_repost_user_id()
    if vk_user_id is None:
        return vk_ok_response()

    target_post_external_ids = data.get_reposted_wall_post_external_ids()
    if not target_post_external_ids:
        return vk_ok_response()

    result = await interactor(
        command_data=CompleteVKRepostTaskCommand(
            event_id=data.event_id,
            vk_user_id=vk_user_id,
            repost_external_id=data.get_repost_external_id(),
            target_post_external_ids=target_post_external_ids,
        ),
    )
    if result.status == TaskCompletionResultStatus.COMPLETED:
        await _send_repost_reward_message(
            data=data,
            result=result,
            message_client=message_client,
        )
        if result.level_up is not None and result.users_id is not None:
            await send_vk_user_message(
                data=data,
                vk_user_id=result.vk_user_id,
                users_id=result.users_id,
                message=build_level_up_message(
                    new_level=result.level_up,
                    level_name=get_level_name(result.level_up),
                    balance_points=result.balance_points or 0,
                ),
                message_client=message_client,
                log_message="Сообщение о новом уровне (репост)",
            )
        await send_week_completion_reward_if_needed(
            data=data,
            vk_user_id=result.vk_user_id,
            users_id=result.users_id,
            week_number=result.week_completion_week_number,
            points_awarded=result.week_completion_points_awarded,
            balance_points=result.week_completion_balance_points,
            level_up=result.week_completion_level_up,
            message_client=message_client,
        )
        await send_project_completion_reward_if_needed(
            data=data,
            vk_user_id=result.vk_user_id,
            users_id=result.users_id,
            points_awarded=result.project_completion_points_awarded,
            balance_points=result.project_completion_balance_points,
            level_up=result.project_completion_level_up,
            message_client=message_client,
        )

    # При репосте VK автоматически ставит лайк на исходный пост, не присылая
    # отдельный like_add callback. Засчитываем лайк явно по тем же external_id.
    like_result = await interactor_like(
        command_data=CompleteVKLikeTaskCommand(
            event_id=data.event_id,
            vk_user_id=vk_user_id,
            liked_post_external_ids=target_post_external_ids,
        ),
    )
    if like_result.status == TaskCompletionResultStatus.COMPLETED:
        await _send_like_reward_message(
            data=data,
            result=like_result,
            message_client=message_client,
        )
        if like_result.level_up is not None and like_result.users_id is not None:
            await send_vk_user_message(
                data=data,
                vk_user_id=like_result.vk_user_id,
                users_id=like_result.users_id,
                message=build_level_up_message(
                    new_level=like_result.level_up,
                    level_name=get_level_name(like_result.level_up),
                    balance_points=like_result.balance_points or 0,
                ),
                message_client=message_client,
                log_message="Сообщение о новом уровне (лайк при репосте)",
            )
        await send_week_completion_reward_if_needed(
            data=data,
            vk_user_id=like_result.vk_user_id,
            users_id=like_result.users_id,
            week_number=like_result.week_completion_week_number,
            points_awarded=like_result.week_completion_points_awarded,
            balance_points=like_result.week_completion_balance_points,
            level_up=like_result.week_completion_level_up,
            message_client=message_client,
        )
        await send_project_completion_reward_if_needed(
            data=data,
            vk_user_id=like_result.vk_user_id,
            users_id=like_result.users_id,
            points_awarded=like_result.project_completion_points_awarded,
            balance_points=like_result.project_completion_balance_points,
            level_up=like_result.project_completion_level_up,
            message_client=message_client,
        )

    return vk_ok_response()


async def _send_like_reward_message(
    *,
    data: VKCallbackPayload,
    result: TaskCompletionResult,
    message_client: IVKMessageClient,
) -> None:
    if result.users_id is None or result.balance_points is None:
        return

    message = build_like_reward_message(
        points_awarded=result.points_awarded,
        balance_points=result.balance_points,
    )
    await send_vk_user_message(
        data=data,
        vk_user_id=result.vk_user_id,
        users_id=result.users_id,
        message=message,
        message_client=message_client,
        log_message="Сообщение о награде за лайк (при репосте) VK",
    )


async def _send_repost_reward_message(
    *,
    data: VKCallbackPayload,
    result: TaskCompletionResult,
    message_client: IVKMessageClient,
) -> None:
    if result.users_id is None or result.balance_points is None:
        return

    message = build_repost_reward_message(
        points_awarded=result.points_awarded,
        balance_points=result.balance_points,
    )
    await send_vk_user_message(
        data=data,
        vk_user_id=result.vk_user_id,
        users_id=result.users_id,
        message=message,
        message_client=message_client,
        log_message="Сообщение о награде за репост VK",
    )
