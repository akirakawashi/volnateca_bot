from presentation.http.routers.v1.routers.vk_callbacks.outbound.messages.template import (
    VKMessageText,
    build_template_message,
)


def build_week_completion_reward_message(
    *,
    week_number: int,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return build_template_message(
        "week_completion_reward",
        week_number=week_number,
        points_awarded=points_awarded,
        balance_points=balance_points,
    )


def build_project_completion_reward_message(
    *,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return build_template_message(
        "project_completion_reward",
        points_awarded=points_awarded,
        balance_points=balance_points,
    )


def build_monthly_top_reward_message(
    *,
    rank: int,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return build_template_message(
        "monthly_top_reward",
        rank=rank,
        points_awarded=points_awarded,
        balance_points=balance_points,
    )


def build_level_up_message(*, new_level: int, level_name: str, balance_points: int) -> VKMessageText:
    return build_template_message(
        "level_up",
        new_level=new_level,
        level_name=level_name,
        balance_points=balance_points,
    )
