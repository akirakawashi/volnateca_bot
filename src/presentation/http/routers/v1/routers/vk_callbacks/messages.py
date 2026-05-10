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
            f"Ты в Волнатеке.\n"
            f"Начислили {bonus_points} {POINTS_SIGN} за старт.\n"
            f"Баланс: {balance_points} {POINTS_SIGN}."
        ),
    )


def build_task_accrual_message(
    *,
    task_name: str,
    points_awarded: int,
    balance_points: int | None,
) -> VKMessageText:
    lines = [
        f"Задание выполнено: {task_name}.",
        f"Начислили {points_awarded} {POINTS_SIGN}.",
    ]
    if balance_points is not None:
        lines.append(f"Баланс: {balance_points} {POINTS_SIGN}.")
    return VKMessageText(text="\n".join(lines))


def build_balance_message(*, balance_points: int) -> VKMessageText:
    return VKMessageText(text=f"Баланс: {balance_points} {POINTS_SIGN}.")


def _build_greeting(*, first_name: str | None) -> str:
    clean_first_name = first_name.strip() if first_name is not None else ""
    if clean_first_name:
        return f"Привет, {clean_first_name}!"
    return "Привет!"


__all__ = [
    "VKMessageText",
    "build_balance_message",
    "build_registration_welcome_message",
    "build_task_accrual_message",
]
