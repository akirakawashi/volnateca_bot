from application.command.record_vk_user_activity import RecordVKUserActivityDTO
from application.interface.clients import IVKMessageClient
from domain.services.level import get_level_name
from presentation.http.routers.v1.routers.vk_callbacks.message_sender import send_vk_user_message
from presentation.http.routers.v1.routers.vk_callbacks.messages import (
    build_daily_streak_reward_message,
    build_level_up_message,
    build_monthly_top_reward_message,
    build_project_completion_reward_message,
    build_quiz_streak_reward_message,
    build_week_completion_reward_message,
)
from presentation.http.routers.v1.routers.vk_callbacks.payload import VKCallbackPayload


async def send_week_completion_reward_if_needed(
    *,
    data: VKCallbackPayload,
    vk_user_id: int,
    users_id: int | None,
    week_number: int | None,
    points_awarded: int,
    balance_points: int | None,
    level_up: int | None,
    message_client: IVKMessageClient,
) -> None:
    if users_id is None or week_number is None or points_awarded <= 0 or balance_points is None:
        return

    await send_vk_user_message(
        data=data,
        vk_user_id=vk_user_id,
        users_id=users_id,
        message=build_week_completion_reward_message(
            week_number=week_number,
            points_awarded=points_awarded,
            balance_points=balance_points,
        ),
        message_client=message_client,
        log_message="Сообщение о бонусе за выполнение всех заданий недели VK",
    )

    if level_up is not None:
        await send_vk_user_message(
            data=data,
            vk_user_id=vk_user_id,
            users_id=users_id,
            message=build_level_up_message(
                new_level=level_up,
                level_name=get_level_name(level_up),
                balance_points=balance_points,
            ),
            message_client=message_client,
            log_message="Сообщение о новом уровне (бонус недели)",
        )


async def send_daily_streak_rewards_if_needed(
    *,
    data: VKCallbackPayload,
    result: RecordVKUserActivityDTO,
    message_client: IVKMessageClient,
) -> None:
    if result.users_id is None:
        return

    for award in result.awards:
        if award.balance_points is None:
            continue

        await send_vk_user_message(
            data=data,
            vk_user_id=result.vk_user_id,
            users_id=result.users_id,
            message=build_daily_streak_reward_message(
                streak_days=award.streak_days,
                points_awarded=award.points_awarded,
                balance_points=award.balance_points,
            ),
            message_client=message_client,
            log_message="Сообщение о бонусе за ежедневный стрик VK",
        )

        if award.level_up is not None:
            await send_vk_user_message(
                data=data,
                vk_user_id=result.vk_user_id,
                users_id=result.users_id,
                message=build_level_up_message(
                    new_level=award.level_up,
                    level_name=get_level_name(award.level_up),
                    balance_points=award.balance_points,
                ),
                message_client=message_client,
                log_message="Сообщение о новом уровне (ежедневный стрик)",
            )


async def send_quiz_streak_reward_if_needed(
    *,
    data: VKCallbackPayload,
    vk_user_id: int,
    users_id: int | None,
    streak_count: int | None,
    points_awarded: int,
    balance_points: int | None,
    level_up: int | None,
    message_client: IVKMessageClient,
) -> None:
    if users_id is None or streak_count is None or points_awarded <= 0 or balance_points is None:
        return

    await send_vk_user_message(
        data=data,
        vk_user_id=vk_user_id,
        users_id=users_id,
        message=build_quiz_streak_reward_message(
            streak_count=streak_count,
            points_awarded=points_awarded,
            balance_points=balance_points,
        ),
        message_client=message_client,
        log_message="Сообщение о бонусе за серию викторин VK",
    )

    if level_up is not None:
        await send_vk_user_message(
            data=data,
            vk_user_id=vk_user_id,
            users_id=users_id,
            message=build_level_up_message(
                new_level=level_up,
                level_name=get_level_name(level_up),
                balance_points=balance_points,
            ),
            message_client=message_client,
            log_message="Сообщение о новом уровне (серия викторин)",
        )


async def send_project_completion_reward_if_needed(
    *,
    data: VKCallbackPayload,
    vk_user_id: int,
    users_id: int | None,
    points_awarded: int,
    balance_points: int | None,
    level_up: int | None,
    message_client: IVKMessageClient,
) -> None:
    if users_id is None or points_awarded <= 0 or balance_points is None:
        return

    await send_vk_user_message(
        data=data,
        vk_user_id=vk_user_id,
        users_id=users_id,
        message=build_project_completion_reward_message(
            points_awarded=points_awarded,
            balance_points=balance_points,
        ),
        message_client=message_client,
        log_message="Сообщение о финальном бонусе за 12 недель VK",
    )

    if level_up is not None:
        await send_vk_user_message(
            data=data,
            vk_user_id=vk_user_id,
            users_id=users_id,
            message=build_level_up_message(
                new_level=level_up,
                level_name=get_level_name(level_up),
                balance_points=balance_points,
            ),
            message_client=message_client,
            log_message="Сообщение о новом уровне (12 недель)",
        )


async def send_monthly_top_reward_if_needed(
    *,
    data: VKCallbackPayload,
    vk_user_id: int,
    users_id: int | None,
    rank: int,
    points_awarded: int,
    balance_points: int | None,
    level_up: int | None,
    message_client: IVKMessageClient,
) -> None:
    if users_id is None or points_awarded <= 0 or balance_points is None:
        return

    await send_vk_user_message(
        data=data,
        vk_user_id=vk_user_id,
        users_id=users_id,
        message=build_monthly_top_reward_message(
            rank=rank,
            points_awarded=points_awarded,
            balance_points=balance_points,
        ),
        message_client=message_client,
        log_message="Сообщение о бонусе за топ-10 месяца VK",
    )

    if level_up is not None:
        await send_vk_user_message(
            data=data,
            vk_user_id=vk_user_id,
            users_id=users_id,
            message=build_level_up_message(
                new_level=level_up,
                level_name=get_level_name(level_up),
                balance_points=balance_points,
            ),
            message_client=message_client,
            log_message="Сообщение о новом уровне (топ-10 месяца)",
        )


__all__ = [
    "send_daily_streak_rewards_if_needed",
    "send_monthly_top_reward_if_needed",
    "send_project_completion_reward_if_needed",
    "send_quiz_streak_reward_if_needed",
    "send_week_completion_reward_if_needed",
]
