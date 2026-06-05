from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class MessageTemplateDefinition:
    code: str
    description: str
    default_template: str
    variables: tuple[str, ...] = ()


MESSAGE_TEMPLATE_DEFINITIONS: dict[str, MessageTemplateDefinition] = {
    "consent_request": MessageTemplateDefinition(
        code="consent_request",
        description="Запрос согласия с условиями конфиденциальности и правилами",
        default_template=(
            "Привет, добро пожаловать в Волнатеку. "
            "Чтобы начать игру, ознакомься с условиями конфиденциальности и правилами ☺️\n\n"
            "[ссылка на оферту]\n\n"
            "После ознакомления, нажми кнопку «Ознакомлен»."
        ),
    ),

    "registration_welcome": MessageTemplateDefinition(
        code="registration_welcome",
        description="Приветственное сообщение после регистрации",
        default_template=(
            "{greeting}\n"
            "Ты в игре!\n\n"
            "Каждую неделю здесь появляются новые задания.\n"
            "За выполнение заданий начисляются баллы.\n"
            "Их можно копить и обменивать на подарки из Банка призов. "
            "Чем больше заданий пройдено, тем ближе самые ценные награды. 💡\n\n"
            "Обрати внимание:\n"
            "• каждую активность можно пройти только один раз;\n"
            "• за специальные задания от партнёров начисляется больше баллов;\n"
            "• количество подарков ограничено;\n"
            "• самые ценные награды достанутся самым вовлечённым участникам. 🏆\n\n"
            "Собирай баллы, следи за новыми активностями и выбирай призы, которые нравятся именно тебе. "
            "Удачи! Задания первой недели уже доступны 👇\n\n"
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
            "Поздравляем, ты подписался на самое классное сообщество, "
            "будем рады видеть твои сердечки на наших постах! 😉\n\n"
            "+{points_awarded} ✦ за подписку\n\n"
            "💫 Баланс: {balance_points} ✦"
        ),
        variables=("points_awarded", "balance_points"),
    ),

    "like_reward": MessageTemplateDefinition(
        code="like_reward",
        description="Сообщение о награде за лайк",
        default_template=(
            "Как приятно получать лайки, ставь сердечки почаще 🫶\n"
            "Лайк засчитан\n\n"
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
            "На наш телефон пришло новое уведомление, кажется это твой комментарий ![😏]\n\n"
            "Комментарий засчитан\n\n"
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

    "tasks_navigation": MessageTemplateDefinition(
        code="tasks_navigation",
        description="Панель управления каруселью заданий",
        default_template="🎯 Панель заданий\n",
        variables=("page", "total_pages"),
    ),

    "tasks_carousel": MessageTemplateDefinition(
        code="tasks_carousel",
        description="Текст над каруселью заданий",
        default_template=(
            "Доступно: {available_count}\n"
            "Страница {page} из {total_pages}\n\n"
            "Листай карточки →"
        ),
        variables=("available_count", "page", "total_pages"),
    ),

    "task_info": MessageTemplateDefinition(
        code="task_info",
        description="Детали задания из карусели",
        default_template="{task_name}\n+{points} ✦{action_url_block}",
        variables=("task_name", "points", "action_url_block"),
    ),

    "custom_promo_task_start": MessageTemplateDefinition(
        code="custom_promo_task_start",
        description="Старт задания с промокодом от Меняйки",
        default_template=(
            "{task_name}\n"
            "+{points} ✦\n\n"
            "Перейди в Меняйку, обменяй ГБ на промокод партнёра и пришли сюда промокод для бота.\n\n"
            "{menyayka_url}\n\n"
            "Жду промокод"
        ),
        variables=("task_name", "points", "menyayka_url"),
    ),

    "custom_promo_invalid_code": MessageTemplateDefinition(
        code="custom_promo_invalid_code",
        description="Неверный промокод для задания Меняйки",
        default_template=(
            "Код неверный.\n\n"
            "Проверь ввод и пришли промокод ещё раз или нажми «Выйти»."
        ),
    ),

    "custom_promo_already_completed": MessageTemplateDefinition(
        code="custom_promo_already_completed",
        description="Промокодное задание уже засчитано",
        default_template=(
            "Этот промокод уже засчитан.\n\n"
            "Открой 🎯 Задания, чтобы выбрать другое задание."
        ),
    ),

    "custom_promo_canceled": MessageTemplateDefinition(
        code="custom_promo_canceled",
        description="Выход из ожидания промокода для задания Меняйки",
        default_template="Вышли из задания. Его можно открыть снова в 🎯 Заданиях.",
    ),

    "store_catalog_navigation": MessageTemplateDefinition(
        code="store_catalog_navigation",
        description="Панель управления каруселью магазина",
        default_template="🎁 Панель магазина\n",
        variables=("section_label", "page", "total_pages"),
    ),

    "store_catalog_carousel": MessageTemplateDefinition(
        code="store_catalog_carousel",
        description="Текст над каруселью магазина",
        default_template=(
            "Раздел: {section_label}\n"
            "Доступно призов: {total_items}\n"
            "💫 Баланс: {balance_points} ✦\n"
            "Страница {page} из {total_pages}\n\n"
            "Листай карточки и нажимай «Открыть», чтобы посмотреть приз."
        ),
        variables=("section_label", "total_items", "balance_points", "page", "total_pages"),
    ),

    "store_pickup_success": MessageTemplateDefinition(
        code="store_pickup_success",
        description="Успешная покупка приза и код самовывоза",
        default_template=(
            "✅ {prize_name}\n\n"
            "Списано: {points_spent} ✦\n"
            "Баланс: {balance_points} ✦\n\n"
            "Код для пункта выдачи: {redemption_code}\n\n"
            "Покажи этот код при самовывозе. Статус заявки — в разделе «Мои призы»."
        ),
        variables=("prize_name", "points_spent", "balance_points", "redemption_code"),
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

    "quiz_failed": MessageTemplateDefinition(
        code="quiz_failed",
        description="Сообщение о завершении викторины без награды",
        default_template=(
            "❌ Квиз завершён без награды.\n\n"
            "Баллы начисляются только если все ответы правильные."
        ),
    ),

    "referral_link": MessageTemplateDefinition(
        code="referral_link",
        description="Сообщение с реферальной ссылкой",
        default_template=(
            "🤝 Пригласить друга\n\n"
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
