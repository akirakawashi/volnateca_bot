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


def build_comment_reward_message(
    *,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return VKMessageText(
        text=(
            "✅ Комментарий засчитан\n"
            "Ты оставил комментарий под записью Волны.\n\n"
            f"+{points_awarded} {POINTS_SIGN} за комментарий\n\n"
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
            f"🧠 Доступна викторина: {task_name}\n\n"
            "Ответь на вопросы викторины и получи баллы.\n"
            "После прохождения покажу следующую доступную викторину.\n\n"
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


def build_quiz_unavailable_message() -> VKMessageText:
    return VKMessageText(
        text=(
            "⏳ Эта викторина уже недоступна.\n\n"
            "Открой 🎯 Задания, чтобы увидеть актуальные активности."
        ),
    )


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


def build_referral_link_message(*, vk_user_id: int, group_id: int) -> VKMessageText:
    link = f"https://vk.com/write-{group_id}?ref={vk_user_id}"
    return VKMessageText(
        text=(
            "🤝 Рефералка\n\n"
            "Пригласи друзей в Волнатеку и получай бонусы:\n\n"
            f"• +30 {POINTS_SIGN} за каждого друга\n"
            f"• +100 {POINTS_SIGN} за 3 друзей\n"
            f"• +200 {POINTS_SIGN} за 5 друзей\n"
            f"• +400 {POINTS_SIGN} за 10 друзей\n\n"
            f"Твоя ссылка:\n{link}"
        ),
    )


def build_referral_bonus_message(
    *,
    bonus_points: int,
    balance_points: int,
) -> VKMessageText:
    return VKMessageText(
        text=(
            "🎉 Новый друг зарегистрировался по твоей ссылке!\n\n"
            f"+{bonus_points} {POINTS_SIGN} за приглашение\n\n"
            f"💫 Баланс: {balance_points} {POINTS_SIGN}"
        ),
    )


def build_referral_milestone_message(
    *,
    milestone_count: int,
    bonus_points: int,
    balance_points: int,
) -> VKMessageText:
    return VKMessageText(
        text=(
            f"🏆 Достижение: {milestone_count} приглашённых друзей!\n\n"
            f"+{bonus_points} {POINTS_SIGN} бонус\n\n"
            f"💫 Баланс: {balance_points} {POINTS_SIGN}"
        ),
    )


def build_week_completion_reward_message(
    *,
    week_number: int,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return VKMessageText(
        text=(
            f"🏆 Все задания недели {week_number} выполнены!\n\n"
            f"+{points_awarded} {POINTS_SIGN} бонус\n\n"
            f"💫 Баланс: {balance_points} {POINTS_SIGN}"
        ),
    )


def build_daily_streak_reward_message(
    *,
    streak_days: int,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return VKMessageText(
        text=(
            f"🔥 Стрик {streak_days} дней!\n\n"
            f"+{points_awarded} {POINTS_SIGN} бонус\n\n"
            f"💫 Баланс: {balance_points} {POINTS_SIGN}"
        ),
    )


def build_quiz_streak_reward_message(
    *,
    streak_count: int,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return VKMessageText(
        text=(
            f"🏆 {streak_count} викторин подряд без ошибок!\n\n"
            f"+{points_awarded} {POINTS_SIGN} бонус\n\n"
            f"💫 Баланс: {balance_points} {POINTS_SIGN}"
        ),
    )


def build_project_completion_reward_message(
    *,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return VKMessageText(
        text=(
            "🏆 Все 12 недель проекта пройдены!\n\n"
            f"+{points_awarded} {POINTS_SIGN} финальный бонус\n\n"
            f"💫 Баланс: {balance_points} {POINTS_SIGN}"
        ),
    )


def build_monthly_top_reward_message(
    *,
    rank: int,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return VKMessageText(
        text=(
            f"🏆 Ты в топ-10 месяца!\n\n"
            f"Место: #{rank}\n\n"
            f"+{points_awarded} {POINTS_SIGN} бонус за топ-10 месяца\n\n"
            f"💫 Баланс: {balance_points} {POINTS_SIGN}"
        ),
    )


def build_level_up_message(*, new_level: int, level_name: str, balance_points: int) -> VKMessageText:
    return VKMessageText(
        text=(
            f"🌊 Новый уровень!\n\n"
            f"Уровень {new_level} — {level_name}\n\n"
            f"💫 Баланс: {balance_points} {POINTS_SIGN}"
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
    "build_comment_reward_message",
    "build_daily_streak_reward_message",
    "build_free_text_fallback_message",
    "build_help_message",
    "build_level_up_message",
    "build_like_reward_message",
    "build_monthly_top_reward_message",
    "build_quiz_answer_result_message",
    "build_quiz_completed_message",
    "build_quiz_offer_message",
    "build_quiz_question_message",
    "build_project_completion_reward_message",
    "build_quiz_streak_reward_message",
    "build_quiz_unavailable_message",
    "build_referral_bonus_message",
    "build_referral_link_message",
    "build_referral_milestone_message",
    "build_registration_welcome_message",
    "build_repost_reward_message",
    "build_subscription_reward_message",
    "build_task_accrual_message",
    "build_tasks_message",
    "build_week_completion_reward_message",
]
