from fastapi.responses import PlainTextResponse

from application.command.complete_vk_repost_task import (
    CompleteVKRepostTaskCommand,
    CompleteVKRepostTaskHandler,
)
from application.common.dto.task import TaskCompletionResult, TaskCompletionResultStatus
from application.interface.clients import IVKMessageClient
from domain.services.level import get_level_name
from presentation.http.routers.v1.routers.vk_callbacks.messages import (
    build_level_up_message,
    build_repost_reward_message,
)
from presentation.http.routers.v1.routers.vk_callbacks.message_sender import send_vk_user_message
from presentation.http.routers.v1.routers.vk_callbacks.payload import VKCallbackPayload
from presentation.http.routers.v1.routers.vk_callbacks.responses import vk_ok_response


async def handle_repost_callback(
    data: VKCallbackPayload,
    interactor: CompleteVKRepostTaskHandler,
    message_client: IVKMessageClient,
) -> PlainTextResponse:
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
    return vk_ok_response()


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
