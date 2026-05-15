from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class MessageTemplateDefinition:
    code: str
    description: str
    default_template: str
    variables: tuple[str, ...] = ()


MESSAGE_TEMPLATE_DEFINITIONS: dict[str, MessageTemplateDefinition] = {
    "registration_welcome": MessageTemplateDefinition(
        code="registration_welcome",
        description="Приветственное сообщение после регистрации",
        default_template=(
            "{greeting}\n"
            "🌊 Добро пожаловать в Волнатеку!\n\n"
            "✅ Регистрация завершена\n"
            "+{bonus_points} ✦ за старт\n\n"
            "💫 Баланс: {balance_points} ✦"
        ),
        variables=("greeting", "bonus_points", "balance_points"),
    ),

    "task_accrual": MessageTemplateDefinition(
        code="task_accrual",
        description="Универсальное сообщение о зачёте задания",
        default_template="✅ Задание выполнено\n{task_name}\n\n+{points_awarded} ✦{balance_line}",
        variables=("task_name", "points_awarded", "balance_line"),
    ),

    "subscription_reward": MessageTemplateDefinition(
        code="subscription_reward",
        description="Сообщение о награде за подписку",
        default_template=(
            "✅ Подписка засчитана\n"
            "Ты подписан на группу Волны.\n\n"
            "+{points_awarded} ✦ за подписку\n\n"
            "💫 Баланс: {balance_points} ✦"
        ),
        variables=("points_awarded", "balance_points"),
    ),

    "like_reward": MessageTemplateDefinition(
        code="like_reward",
        description="Сообщение о награде за лайк",
        default_template=(
            "✅ Лайк засчитан\n"
            "Ты поставил лайк записи Волны.\n\n"
            "+{points_awarded} ✦ за лайк\n\n"
            "💫 Баланс: {balance_points} ✦"
        ),
        variables=("points_awarded", "balance_points"),
    ),

    "repost_reward": MessageTemplateDefinition(
        code="repost_reward",
        description="Сообщение о награде за репост",
        default_template=(
            "✅ Репост засчитан\n"
            "Ты сделал репост записи Волны.\n\n"
            "+{points_awarded} ✦ за репост\n\n"
            "💫 Баланс: {balance_points} ✦"
        ),
        variables=("points_awarded", "balance_points"),
    ),

    "comment_reward": MessageTemplateDefinition(
        code="comment_reward",
        description="Сообщение о награде за комментарий",
        default_template=(
            "✅ Комментарий засчитан\n"
            "Ты оставил комментарий под записью Волны.\n\n"
            "+{points_awarded} ✦ за комментарий\n\n"
            "💫 Баланс: {balance_points} ✦"
        ),
        variables=("points_awarded", "balance_points"),
    ),

    "balance": MessageTemplateDefinition(
        code="balance",
        description="Сообщение с текущим балансом",
        default_template="💫 Баланс\n\n{balance_points} ✦",
        variables=("balance_points",),
    ),

    "tasks_empty": MessageTemplateDefinition(
        code="tasks_empty",
        description="Сообщение при отсутствии активных заданий",
        default_template="🎯 Ваши активные задания\n\nСейчас активных заданий нет.",
    ),

    "tasks_list": MessageTemplateDefinition(
        code="tasks_list",
        description="Список активных заданий",
        default_template="🎯 Ваши активные задания\n\n{tasks_block}",
        variables=("tasks_block",),
    ),

    "help": MessageTemplateDefinition(
        code="help",
        description="Справка по меню",
        default_template=(
            "🌊 Меню Волнатеки\n\n"
            "💫 Баланс — покажу твои дискошары\n"
            "🎯 Задания — покажу активности проекта\n"
            "🎁 Магазин — покажу призы\n"
            "🤝 Рефералка — покажу ссылку для друзей"
        ),
    ),

    "quiz_offer": MessageTemplateDefinition(
        code="quiz_offer",
        description="Предложение начать викторину",
        default_template=(
            "🧠 Доступна викторина: {task_name}\n\n"
            "Ответь на вопросы викторины и получи баллы.\n"
            "После прохождения покажу следующую доступную викторину.\n\n"
            "Награда: +{points} ✦\n\n"
            "Хочешь пройти квиз прямо сейчас?"
        ),
        variables=("task_name", "points"),
    ),

    "quiz_question": MessageTemplateDefinition(
        code="quiz_question",
        description="Текст вопроса викторины",
        default_template="🧠 Вопрос {question_number} из {total_questions}\n\n{question_text}",
        variables=("question_number", "total_questions", "question_text"),
    ),

    "quiz_answer_correct": MessageTemplateDefinition(
        code="quiz_answer_correct",
        description="Сообщение о правильном ответе на вопрос викторины",
        default_template="✅ Верно!",
    ),

    "quiz_answer_incorrect": MessageTemplateDefinition(
        code="quiz_answer_incorrect",
        description="Сообщение о неправильном ответе на вопрос викторины",
        default_template="❌ Неверно.{correct_hint}",
        variables=("correct_hint",),
    ),

    "quiz_unavailable": MessageTemplateDefinition(
        code="quiz_unavailable",
        description="Сообщение о недоступной викторине",
        default_template="⏳ Эта викторина уже недоступна.\n\nОткрой 🎯 Задания, чтобы увидеть актуальные активности.",
    ),

    "quiz_completed": MessageTemplateDefinition(
        code="quiz_completed",
        description="Сообщение о завершении викторины",
        default_template="🎉 Квиз пройден!\n\n+{points_awarded} ✦ за квиз\n\n💫 Баланс: {balance_points} ✦",
        variables=("points_awarded", "balance_points"),
    ),

    "free_text_fallback": MessageTemplateDefinition(
        code="free_text_fallback",
        description="Ответ на нераспознанный свободный текст",
        default_template="🤔 Пока я лучше всего понимаю команды:\n\n💫 Баланс\n🎯 Задания\n🎁 Магазин\n🤝 Рефералка",
    ),

    "referral_link": MessageTemplateDefinition(
        code="referral_link",
        description="Сообщение с реферальной ссылкой",
        default_template=(
            "🤝 Рефералка\n\n"
            "Пригласи друзей в Волнатеку и получай бонусы:\n\n"
            "• +30 ✦ за каждого друга\n"
            "• +100 ✦ за 3 друзей\n"
            "• +200 ✦ за 5 друзей\n"
            "• +400 ✦ за 10 друзей\n\n"
            "Твоя ссылка:\n{link}"
        ),
        variables=("link",),
    ),

    "referral_bonus": MessageTemplateDefinition(
        code="referral_bonus",
        description="Сообщение о бонусе за регистрацию друга",
        default_template=(
            "🎉 Новый друг зарегистрировался по твоей ссылке!\n\n"
            "+{bonus_points} ✦ за приглашение\n\n"
            "💫 Баланс: {balance_points} ✦"
        ),
        variables=("bonus_points", "balance_points"),
    ),

    "referral_milestone": MessageTemplateDefinition(
        code="referral_milestone",
        description="Сообщение о milestone по приглашённым друзьям",
        default_template=(
            "🏆 Достижение: {milestone_count} приглашённых друзей!\n\n"
            "+{bonus_points} ✦ бонус\n\n"
            "💫 Баланс: {balance_points} ✦"
        ),
        variables=("milestone_count", "bonus_points", "balance_points"),
    ),

    "week_completion_reward": MessageTemplateDefinition(
        code="week_completion_reward",
        description="Сообщение о бонусе за выполнение недели",
        default_template=(
            "🏆 Все задания недели {week_number} выполнены!\n\n"
            "+{points_awarded} ✦ бонус\n\n"
            "💫 Баланс: {balance_points} ✦"
        ),
        variables=("week_number", "points_awarded", "balance_points"),
    ),

    "daily_streak_reward": MessageTemplateDefinition(
        code="daily_streak_reward",
        description="Сообщение о бонусе за ежедневный стрик",
        default_template="🔥 Стрик {streak_days} дней!\n\n+{points_awarded} ✦ бонус\n\n💫 Баланс: {balance_points} ✦",
        variables=("streak_days", "points_awarded", "balance_points"),
    ),

    "quiz_streak_reward": MessageTemplateDefinition(
        code="quiz_streak_reward",
        description="Сообщение о бонусе за серию квизов без ошибок",
        default_template=(
            "🏆 {streak_count} викторин подряд без ошибок!\n\n"
            "+{points_awarded} ✦ бонус\n\n"
            "💫 Баланс: {balance_points} ✦"
        ),
        variables=("streak_count", "points_awarded", "balance_points"),
    ),

    "project_completion_reward": MessageTemplateDefinition(
        code="project_completion_reward",
        description="Сообщение о финальном бонусе за проект",
        default_template=(
            "🏆 Все 12 недель проекта пройдены!\n\n"
            "+{points_awarded} ✦ финальный бонус\n\n"
            "💫 Баланс: {balance_points} ✦"
        ),
        variables=("points_awarded", "balance_points"),
    ),

    "monthly_top_reward": MessageTemplateDefinition(
        code="monthly_top_reward",
        description="Сообщение о бонусе за monthly top",
        default_template=(
            "🏆 Ты в топ-10 месяца!\n\n"
            "Место: #{rank}\n\n"
            "+{points_awarded} ✦ бонус за топ-10 месяца\n\n"
            "💫 Баланс: {balance_points} ✦"
        ),
        variables=("rank", "points_awarded", "balance_points"),
    ),
    
    "level_up": MessageTemplateDefinition(
        code="level_up",
        description="Сообщение о новом уровне",
        default_template=(
            "🌊 Новый уровень!\n\nУровень {new_level} — {level_name}\n\n💫 Баланс: {balance_points} ✦"
        ),
        variables=("new_level", "level_name", "balance_points"),
    ),
}


def get_message_template_definition(code: str) -> MessageTemplateDefinition | None:
    return MESSAGE_TEMPLATE_DEFINITIONS.get(code)


def list_message_template_definitions() -> tuple[MessageTemplateDefinition, ...]:
    return tuple(MESSAGE_TEMPLATE_DEFINITIONS.values())


__all__ = [
    "MESSAGE_TEMPLATE_DEFINITIONS",
    "MessageTemplateDefinition",
    "get_message_template_definition",
    "list_message_template_definitions",
]
