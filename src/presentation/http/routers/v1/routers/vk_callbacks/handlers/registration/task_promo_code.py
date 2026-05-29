from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionDTO,
)
from application.command.task_promo_code import (
    ActivateTaskPromoCodeCommand,
    ActivateTaskPromoCodeHandler,
    CancelTaskPromoCodeCommand,
    CancelTaskPromoCodeHandler,
    StartTaskPromoCodeCommand,
    StartTaskPromoCodeHandler,
    TaskPromoCodeFlowStatus,
)
from application.common.dto.task import TaskCompletionResult, TaskCompletionResultStatus
from application.interface.clients import IVKMessageClient
from domain.services.level import get_level_name
from presentation.http.routers.v1.routers.vk_callbacks.handlers.achievement import (
    send_project_completion_reward_if_needed,
    send_week_completion_reward_if_needed,
)
from presentation.http.routers.v1.routers.vk_callbacks.outbound.keyboards import (
    build_main_menu_keyboard,
    build_task_promo_code_wait_keyboard,
)
from presentation.http.routers.v1.routers.vk_callbacks.outbound.messages import (
    build_custom_promo_canceled_message,
    build_custom_promo_invalid_code_message,
    build_custom_promo_task_start_message,
    build_level_up_message,
    build_task_accrual_message,
)
from presentation.http.routers.v1.routers.vk_callbacks.outbound.sender import send_vk_user_message
from presentation.http.routers.v1.routers.vk_callbacks.protocol.payload import VKCallbackPayload


async def handle_task_promo_code_start(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    tasks_id: int,
    message_client: IVKMessageClient,
    start_task_promo_code_interactor: StartTaskPromoCodeHandler,
) -> None:
    started = await start_task_promo_code_interactor(
        command_data=StartTaskPromoCodeCommand(
            vk_user_id=result.registration.vk_user_id,
            tasks_id=tasks_id,
        ),
    )
    if started.status != TaskPromoCodeFlowStatus.STARTED:
        return
    if started.task_name is None or started.points is None:
        return

    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=build_custom_promo_task_start_message(
            task_name=started.task_name,
            points=started.points,
        ),
        keyboard=build_task_promo_code_wait_keyboard(),
        message_client=message_client,
        log_message="Старт задания с промокодом VK",
    )


async def handle_task_promo_code_text(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    message_client: IVKMessageClient,
    activate_task_promo_code_interactor: ActivateTaskPromoCodeHandler,
) -> bool:
    handled = await activate_task_promo_code_interactor(
        command_data=ActivateTaskPromoCodeCommand(
            event_id=data.event_id,
            vk_user_id=result.registration.vk_user_id,
            promo_code=data.get_message_text(),
        ),
    )
    if handled.status == TaskPromoCodeFlowStatus.NO_ACTIVE_WAIT:
        return False

    if handled.status == TaskPromoCodeFlowStatus.INVALID_CODE:
        await _send_task_promo_invalid_code_message(
            data=data,
            result=result,
            message_client=message_client,
        )
        return True

    if handled.completion is not None:
        await _send_task_promo_completion_messages(
            data=data,
            completion=handled.completion,
            message_client=message_client,
        )
        return True

    return True


async def handle_task_promo_code_exit(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    message_client: IVKMessageClient,
    cancel_task_promo_code_interactor: CancelTaskPromoCodeHandler,
) -> None:
    canceled = await cancel_task_promo_code_interactor(
        command_data=CancelTaskPromoCodeCommand(vk_user_id=result.registration.vk_user_id),
    )
    if canceled.status == TaskPromoCodeFlowStatus.NO_ACTIVE_WAIT:
        return

    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=build_custom_promo_canceled_message(),
        keyboard=build_main_menu_keyboard(),
        message_client=message_client,
        log_message="Выход из ожидания промокода VK",
    )


async def _send_task_promo_invalid_code_message(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    message_client: IVKMessageClient,
) -> None:
    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=build_custom_promo_invalid_code_message(),
        keyboard=build_main_menu_keyboard(),
        message_client=message_client,
        log_message="Неверный промокод задания VK",
    )


async def _send_task_promo_completion_messages(
    *,
    data: VKCallbackPayload,
    completion: TaskCompletionResult,
    message_client: IVKMessageClient,
) -> None:
    if completion.status not in (
        TaskCompletionResultStatus.COMPLETED,
        TaskCompletionResultStatus.ALREADY_COMPLETED,
    ):
        return
    if completion.users_id is None or completion.balance_points is None or completion.task_name is None:
        return

    await send_vk_user_message(
        data=data,
        vk_user_id=completion.vk_user_id,
        users_id=completion.users_id,
        message=build_task_accrual_message(
            task_name=completion.task_name,
            points_awarded=completion.points_awarded,
            balance_points=completion.balance_points,
        ),
        keyboard=build_main_menu_keyboard(),
        message_client=message_client,
        log_message="Сообщение о награде за промокод VK",
    )
    if completion.level_up is not None:
        await send_vk_user_message(
            data=data,
            vk_user_id=completion.vk_user_id,
            users_id=completion.users_id,
            message=build_level_up_message(
                new_level=completion.level_up,
                level_name=get_level_name(completion.level_up),
                balance_points=completion.balance_points,
            ),
            message_client=message_client,
            log_message="Сообщение о новом уровне (промокод задания)",
        )
    await send_week_completion_reward_if_needed(
        data=data,
        vk_user_id=completion.vk_user_id,
        users_id=completion.users_id,
        week_number=completion.week_completion_week_number,
        points_awarded=completion.week_completion_points_awarded,
        balance_points=completion.week_completion_balance_points,
        level_up=completion.week_completion_level_up,
        message_client=message_client,
    )
    await send_project_completion_reward_if_needed(
        data=data,
        vk_user_id=completion.vk_user_id,
        users_id=completion.users_id,
        points_awarded=completion.project_completion_points_awarded,
        balance_points=completion.project_completion_balance_points,
        level_up=completion.project_completion_level_up,
        message_client=message_client,
    )
