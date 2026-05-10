from dataclasses import dataclass


POINTS_SIGN = "✦"


@dataclass(slots=True, frozen=True, kw_only=True)
class VKMessageText:
    text: str


def build_registration_welcome_message(
    *,
    first_name: str | None,
    balance_points: int,
    bonus_points: int,
) -> VKMessageText:
    greeting = _build_greeting(first_name=first_name)
    return VKMessageText(
        text=(
            f"{greeting}\n"
            "🌊 Добро пожаловать в Волнатеку!\n\n"
            "✅ Регистрация завершена\n"
            f"+{bonus_points} {POINTS_SIGN} за старт\n\n"
            f"💫 Баланс: {balance_points} {POINTS_SIGN}"
        ),
    )


def build_task_accrual_message(
    *,
    task_name: str,
    points_awarded: int,
    balance_points: int | None,
    ) -> VKMessageText:
    lines = [
        "✅ Задание выполнено",
        task_name,
        "",
        f"+{points_awarded} {POINTS_SIGN}",
    ]
    if balance_points is not None:
        lines.extend(("", f"💫 Баланс: {balance_points} {POINTS_SIGN}"))
    return VKMessageText(text="\n".join(lines))


def build_subscription_reward_message(
    *,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return VKMessageText(
        text=(
            "✅ Подписка засчитана\n"
            "Ты подписан на группу Волны.\n\n"
            f"+{points_awarded} {POINTS_SIGN} за подписку\n\n"
            f"💫 Баланс: {balance_points} {POINTS_SIGN}"
        ),
    )


def build_balance_message(*, balance_points: int) -> VKMessageText:
    return VKMessageText(text=f"💫 Баланс\n\n{balance_points} {POINTS_SIGN}")


def build_help_message() -> VKMessageText:
    return VKMessageText(
        text=(
            "🌊 Меню Волнатеки\n\n"
            "💫 Баланс — покажу твои дискошары\n"
            "🎯 Задания — покажу активности проекта\n"
            "🎁 Магазин — покажу призы\n"
            "🤝 Рефералка — покажу ссылку для друзей"
        ),
    )


def build_free_text_fallback_message() -> VKMessageText:
    return VKMessageText(
        text=(
            "🤔 Пока я лучше всего понимаю команды:\n\n"
            "💫 Баланс\n"
            "🎯 Задания\n"
            "🎁 Магазин\n"
            "🤝 Рефералка"
        ),
    )


def _build_greeting(*, first_name: str | None) -> str:
    clean_first_name = first_name.strip() if first_name is not None else ""
    if clean_first_name:
        return f"Привет, {clean_first_name}!"
    return "Привет!"


__all__ = [
    "VKMessageText",
    "build_balance_message",
    "build_free_text_fallback_message",
    "build_help_message",
    "build_registration_welcome_message",
    "build_subscription_reward_message",
    "build_task_accrual_message",
]
