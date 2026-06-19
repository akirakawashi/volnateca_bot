from presentation.http.routers.v1.routers.vk_callbacks.outbound.messages.template import (
    VKMessageText,
    build_template_message,
)


def build_subscription_reward_message(
    *,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return build_template_message(
        "subscription_reward",
        points_awarded=points_awarded,
        balance_points=balance_points,
    )


def build_like_reward_message(
    *,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return build_template_message(
        "like_reward",
        points_awarded=points_awarded,
        balance_points=balance_points,
    )


def build_comment_reward_message(
    *,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return build_template_message(
        "comment_reward",
        points_awarded=points_awarded,
        balance_points=balance_points,
    )
