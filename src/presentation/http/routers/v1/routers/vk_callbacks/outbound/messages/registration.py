from presentation.http.routers.v1.routers.vk_callbacks.outbound.messages.template import (
    VKMessageText,
    build_greeting,
    build_template_message,
)


def build_registration_welcome_message(
    *,
    first_name: str | None,
    balance_points: int,
    bonus_points: int,
) -> VKMessageText:
    return build_template_message(
        "registration_welcome",
        greeting=build_greeting(first_name=first_name),
        balance_points=balance_points,
        bonus_points=bonus_points,
    )


def build_main_menu_message() -> VKMessageText:
    return VKMessageText(text="Главное меню")


def build_consent_request_message() -> VKMessageText:
    return build_template_message("consent_request")


def build_balance_message(*, balance_points: int) -> VKMessageText:
    return build_template_message("balance", balance_points=balance_points)


def build_referral_link_message(*, vk_user_id: int, group_id: int) -> VKMessageText:
    return build_template_message(
        "referral_link",
        link=f"https://vk.com/write-{group_id}?ref={vk_user_id}",
    )


def build_referral_bonus_message(
    *,
    bonus_points: int,
    balance_points: int,
) -> VKMessageText:
    return build_template_message(
        "referral_bonus",
        bonus_points=bonus_points,
        balance_points=balance_points,
    )


def build_referral_milestone_message(
    *,
    milestone_count: int,
    bonus_points: int,
    balance_points: int,
) -> VKMessageText:
    return build_template_message(
        "referral_milestone",
        milestone_count=milestone_count,
        bonus_points=bonus_points,
        balance_points=balance_points,
    )
