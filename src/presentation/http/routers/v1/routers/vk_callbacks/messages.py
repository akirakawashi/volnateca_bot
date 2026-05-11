from dataclasses import dataclass

from application.common.dto.task import VKUserAvailableTaskDTO


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


def build_like_reward_message(
    *,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return VKMessageText(
        text=(
            "✅ Лайк засчитан\n"
            "Ты поставил лайк записи Волны.\n\n"
            f"+{points_awarded} {POINTS_SIGN} за лайк\n\n"
            f"💫 Баланс: {balance_points} {POINTS_SIGN}"
        ),
    )


def build_repost_reward_message(
    *,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return VKMessageText(
        text=(
            "✅ Репост засчитан\n"
            "Ты сделал репост записи Волны.\n\n"
            f"+{points_awarded} {POINTS_SIGN} за репост\n\n"
            f"💫 Баланс: {balance_points} {POINTS_SIGN}"
        ),
    )


def build_balance_message(*, balance_points: int) -> VKMessageText:
    return VKMessageText(text=f"💫 Баланс\n\n{balance_points} {POINTS_SIGN}")


def build_tasks_message(*, tasks: tuple[VKUserAvailableTaskDTO, ...]) -> VKMessageText:
    if not tasks:
        return VKMessageText(text="🎯 Ваши активные задания\n\nСейчас активных заданий нет.")

    lines = ["🎯 Ваши активные задания"]
    for index, task in enumerate(tasks, start=1):
        lines.extend(
            (
                "",
                f"{index}. {task.task_name}",
                f"+{task.points} {POINTS_SIGN}",
            ),
        )
        if task.action_url is not None:
            lines.append(task.action_url)

    return VKMessageText(text="\n".join(lines))


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


def build_quiz_offer_message(*, task_name: str, points: int) -> VKMessageText:
    return VKMessageText(
        text=(
            f"🧠 {task_name}\n\n"
            "Ответь на вопросы недели и получи баллы!\n\n"
            f"Награда: +{points} {POINTS_SIGN}\n\n"
            "Хочешь пройти квиз прямо сейчас?"
        ),
    )


def build_quiz_question_message(
    *,
    question_text: str,
    question_number: int,
    total_questions: int,
) -> VKMessageText:
    return VKMessageText(
        text=(f"🧠 Вопрос {question_number} из {total_questions}\n\n{question_text}"),
    )


def build_quiz_answer_result_message(
    *,
    is_correct: bool,
    correct_option_text: str | None,
) -> VKMessageText:
    if is_correct:
        return VKMessageText(text="✅ Верно!")
    correct_hint = f"\nПравильный ответ: {correct_option_text}" if correct_option_text else ""
    return VKMessageText(text=f"❌ Неверно.{correct_hint}")


def build_quiz_completed_message(
    *,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return VKMessageText(
        text=(
            "🎉 Квиз пройден!\n\n"
            f"+{points_awarded} {POINTS_SIGN} за квиз\n\n"
            f"💫 Баланс: {balance_points} {POINTS_SIGN}"
        ),
    )


def build_free_text_fallback_message() -> VKMessageText:
    return VKMessageText(
        text=("🤔 Пока я лучше всего понимаю команды:\n\n💫 Баланс\n🎯 Задания\n🎁 Магазин\n🤝 Рефералка"),
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
    "build_like_reward_message",
    "build_quiz_answer_result_message",
    "build_quiz_completed_message",
    "build_quiz_offer_message",
    "build_quiz_question_message",
    "build_registration_welcome_message",
    "build_repost_reward_message",
    "build_subscription_reward_message",
    "build_task_accrual_message",
    "build_tasks_message",
]
