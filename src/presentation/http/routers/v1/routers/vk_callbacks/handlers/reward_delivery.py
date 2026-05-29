from application.common.dto.task import TaskCompletionResult
from application.interface.clients import IVKMessageClient
from presentation.http.routers.v1.routers.vk_callbacks.outbound.messages import build_like_reward_message
from presentation.http.routers.v1.routers.vk_callbacks.outbound.sender import send_vk_user_message
from presentation.http.routers.v1.routers.vk_callbacks.protocol.payload import VKCallbackPayload


async def send_like_reward_message(
    *,
    data: VKCallbackPayload,
    result: TaskCompletionResult,
    message_client: IVKMessageClient,
    log_message: str,
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
        log_message=log_message,
    )
