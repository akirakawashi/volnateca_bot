"""Обработчик реферальной кнопки и пост-регистрационные реферальные уведомления."""

from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionDTO,
)
from application.common.dto.referral import ProcessReferralDTO
from application.interface.clients import IVKMessageClient
from domain.services.level import get_level_name
from presentation.http.routers.v1.routers.vk_callbacks.outbound.sender import send_vk_user_message
from presentation.http.routers.v1.routers.vk_callbacks.outbound.messages import (
    build_level_up_message,
    build_referral_bonus_message,
    build_referral_link_message,
    build_referral_milestone_message,
)
from presentation.http.routers.v1.routers.vk_callbacks.protocol.payload import VKCallbackPayload


async def handle_referral(
    *,
    data: VKCallbackPayload,
    result: RegisterVKUserAndCheckSubscriptionDTO,
    group_id: int,
    message_client: IVKMessageClient,
) -> None:
    await send_vk_user_message(
        data=data,
        vk_user_id=result.registration.vk_user_id,
        users_id=result.registration.users_id,
        message=build_referral_link_message(
            vk_user_id=result.registration.vk_user_id,
            group_id=group_id,
        ),
        message_client=message_client,
        log_message="Реферальная ссылка VK",
    )


async def send_referral_notifications(
    *,
    data: VKCallbackPayload,
    referral_result: ProcessReferralDTO | None,
    message_client: IVKMessageClient,
) -> None:
    """Отправляет уведомления по уже обработанному реферальному результату."""
    if referral_result is None:
        return
    if not referral_result.created or referral_result.inviter_users_id is None:
        return
    if referral_result.inviter_balance_points is None:
        return

    # Уведомляем пригласившего о +30 ✦
    await send_vk_user_message(
        data=data,
        vk_user_id=referral_result.inviter_vk_user_id,
        users_id=referral_result.inviter_users_id,
        message=build_referral_bonus_message(
            bonus_points=referral_result.bonus_points,
            balance_points=referral_result.inviter_balance_points,
        ),
        message_client=message_client,
        log_message="Уведомление о реферальном бонусе VK",
    )

    # Уведомление о новом уровне после реферального бонуса
    if referral_result.level_up is not None:
        await send_vk_user_message(
            data=data,
            vk_user_id=referral_result.inviter_vk_user_id,
            users_id=referral_result.inviter_users_id,
            message=build_level_up_message(
                new_level=referral_result.level_up,
                level_name=get_level_name(referral_result.level_up),
                balance_points=referral_result.inviter_balance_points,
            ),
            message_client=message_client,
            log_message="Уведомление о новом уровне (реферал) VK",
        )

    # Дополнительно уведомляем о milestone-бонусе, если достигнут
    if referral_result.milestone_reached is not None and referral_result.milestone_bonus_points is not None:
        # Баланс после milestone — складываем оба бонуса
        milestone_balance = referral_result.inviter_balance_points
        await send_vk_user_message(
            data=data,
            vk_user_id=referral_result.inviter_vk_user_id,
            users_id=referral_result.inviter_users_id,
            message=build_referral_milestone_message(
                milestone_count=referral_result.milestone_reached,
                bonus_points=referral_result.milestone_bonus_points,
                balance_points=milestone_balance,
            ),
            message_client=message_client,
            log_message="Уведомление о milestone рефералки VK",
        )
