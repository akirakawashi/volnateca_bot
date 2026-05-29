from fastapi.responses import PlainTextResponse

from application.command.complete_vk_poll_task import (
    CompleteVKPollTaskCommand,
    CompleteVKPollTaskHandler,
)
from application.common.dto.task import TaskCompletionResult, TaskCompletionResultStatus
from application.interface.clients import IVKMessageClient
from domain.services.level import get_level_name
from presentation.http.routers.v1.routers.vk_callbacks.handlers.achievement import (
    send_project_completion_reward_if_needed,
    send_week_completion_reward_if_needed,
)
from presentation.http.routers.v1.routers.vk_callbacks.outbound.messages import (
    build_level_up_message,
    build_task_accrual_message,
)
from presentation.http.routers.v1.routers.vk_callbacks.outbound.sender import send_vk_user_message
from presentation.http.routers.v1.routers.vk_callbacks.protocol.payload import VKCallbackPayload
from presentation.http.routers.v1.routers.vk_callbacks.protocol.responses import vk_ok_response


async def handle_poll_vote_callback(
    data: VKCallbackPayload,
    interactor_complete: CompleteVKPollTaskHandler,
    message_client: IVKMessageClient,
) -> PlainTextResponse:
    """Засчитывает голос в опросе и отправляет награду при успешном начислении."""

    voter_id = data.get_poll_user_id()
    if voter_id is None:
        return vk_ok_response()

    voted_poll_external_ids = data.get_voted_poll_external_ids()
    result = await interactor_complete(
        command_data=CompleteVKPollTaskCommand(
            event_id=data.event_id,
            vk_user_id=voter_id,
            voted_poll_external_ids=voted_poll_external_ids,
        ),
    )
    if result.status == TaskCompletionResultStatus.COMPLETED:
        await _send_poll_reward_message(
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
                log_message="Сообщение о новом уровне (опрос)",
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
    return vk_ok_response()


async def _send_poll_reward_message(
    *,
    data: VKCallbackPayload,
    result: TaskCompletionResult,
    message_client: IVKMessageClient,
) -> None:
    if result.users_id is None or result.balance_points is None or result.task_name is None:
        return

    message = build_task_accrual_message(
        task_name=result.task_name,
        points_awarded=result.points_awarded,
        balance_points=result.balance_points,
    )
    await send_vk_user_message(
        data=data,
        vk_user_id=result.vk_user_id,
        users_id=result.users_id,
        message=message,
        message_client=message_client,
        log_message="Сообщение о награде за голосование в опросе VK",
    )
