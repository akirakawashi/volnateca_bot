from dataclasses import dataclass, field

from application.common.dto.store import (
    StoreCatalogDTO,
    StorePrizeCardDTO,
    StorePrizeUserState,
    StorePrizeView,
)
from application.common.dto.task import VKUserAvailableTaskDTO
from application.services.vk_message_template_catalog import get_message_template_definition
from domain.enums.prize import PrizeType


@dataclass(slots=True, frozen=True, kw_only=True)
class VKMessageText:
    text: str
    template_code: str | None = None
    template_context: dict[str, object] = field(default_factory=dict)


def build_registration_welcome_message(
    *,
    first_name: str | None,
    balance_points: int,
    bonus_points: int,
) -> VKMessageText:
    return _template_message(
        "registration_welcome",
        greeting=_build_greeting(first_name=first_name),
        balance_points=balance_points,
        bonus_points=bonus_points,
    )


def build_main_menu_message() -> VKMessageText:
    return VKMessageText(text="Главное меню")


def build_consent_request_message() -> VKMessageText:
    return _template_message("consent_request")


def build_task_accrual_message(
    *,
    task_name: str,
    points_awarded: int,
    balance_points: int | None,
) -> VKMessageText:
    balance_line = f"\n\n💫 Баланс: {balance_points} ✦" if balance_points is not None else ""
    return _template_message(
        "task_accrual",
        task_name=task_name,
        points_awarded=points_awarded,
        balance_line=balance_line,
    )


def build_subscription_reward_message(
    *,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return _template_message(
        "subscription_reward",
        points_awarded=points_awarded,
        balance_points=balance_points,
    )


def build_like_reward_message(
    *,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return _template_message(
        "like_reward",
        points_awarded=points_awarded,
        balance_points=balance_points,
    )


def build_repost_reward_message(
    *,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return _template_message(
        "repost_reward",
        points_awarded=points_awarded,
        balance_points=balance_points,
    )


def build_comment_reward_message(
    *,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return _template_message(
        "comment_reward",
        points_awarded=points_awarded,
        balance_points=balance_points,
    )


def build_balance_message(*, balance_points: int) -> VKMessageText:
    return _template_message("balance", balance_points=balance_points)


def build_tasks_message(*, tasks: tuple[VKUserAvailableTaskDTO, ...]) -> VKMessageText:
    if not tasks:
        return _template_message("tasks_empty")

    blocks: list[str] = []
    for index, task in enumerate(tasks, start=1):
        lines = [
            f"{index}. {task.task_name}",
            f"+{task.points} ✦",
        ]
        if task.action_url is not None:
            lines.append(task.action_url)
        blocks.append("\n".join(lines))

    return _template_message("tasks_list", tasks_block="\n\n".join(blocks))


def build_tasks_carousel_message(*, tasks: tuple[VKUserAvailableTaskDTO, ...]) -> VKMessageText:
    return VKMessageText(
        text=(
            f"🎯 Задания\n\n"
            f"Доступно: {len(tasks)}\n\n"
            "Листай карточки →"
        ),
    )


def build_task_info_message(*, task: VKUserAvailableTaskDTO) -> VKMessageText:
    lines = [
        task.task_name,
        f"+{task.points} ✦",
    ]
    if task.action_url is not None:
        lines.append(f"\n{task.action_url}")
    return VKMessageText(text="\n".join(lines))


def build_store_root_message(*, balance_points: int) -> VKMessageText:
    return VKMessageText(
        text=(
            "🎁 Магазин призов\n\n"
            f"💫 Баланс: {balance_points} ✦\n\n"
            "Выбери раздел каталога:"
        ),
    )


def build_store_catalog_message(*, catalog: StoreCatalogDTO) -> VKMessageText:
    header = (
        f"🎁 Магазин · {catalog.section.label}\n\n"
        f"💫 Баланс: {catalog.balance_points} ✦\n"
        f"Страница {catalog.pagination.page} из {catalog.pagination.total_pages}"
    )
    if not catalog.prizes:
        return VKMessageText(text=f"{header}\n\nВ этом разделе пока нет призов.")

    start_index = (catalog.pagination.page - 1) * catalog.pagination.page_size
    prize_blocks = [
        _build_store_catalog_prize_line(index=start_index + index, prize=prize)
        for index, prize in enumerate(catalog.prizes, start=1)
    ]
    return VKMessageText(text=f"{header}\n\n" + "\n\n".join(prize_blocks))


def build_store_catalog_navigation_message(*, catalog: StoreCatalogDTO) -> VKMessageText:
    return VKMessageText(
        text=(
            f"🎁 Магазин · {catalog.section.label}\n"
            f"Страница {catalog.pagination.page} из {catalog.pagination.total_pages}"
        ),
    )


def build_store_catalog_carousel_message(*, catalog: StoreCatalogDTO) -> VKMessageText:
    return VKMessageText(
        text=(
            f"🎁 Магазин · {catalog.section.label}\n\n"
            f"💫 Баланс: {catalog.balance_points} ✦\n"
            f"Страница {catalog.pagination.page} из {catalog.pagination.total_pages}\n\n"
            "Листай карточки и нажимай «Открыть», чтобы посмотреть приз."
        ),
    )


def build_store_exit_message() -> VKMessageText:
    return VKMessageText(text="Главное меню")


def build_store_prize_card_message(*, card: StorePrizeCardDTO) -> VKMessageText:
    prize = card.prize
    if prize is None:
        return build_store_prize_not_found_message()

    description = _format_optional_description(prize.description)
    return VKMessageText(
        text=(
            f"🎁 {prize.prize_name}\n"
            f"{_format_prize_type(prize.prize_type)}\n\n"
            f"Стоимость: {prize.cost_points} ✦\n"
            f"Баланс: {card.balance_points} ✦\n"
            f"Статус: {_format_store_prize_state(prize)}\n"
            f"Остаток: {_format_prize_quantity(prize)}"
            f"{description}"
        ),
    )


def build_store_prize_not_found_message() -> VKMessageText:
    return VKMessageText(text="🎁 Магазин призов\n\nЭтот приз уже недоступен в каталоге.")


def build_store_claim_unavailable_message(*, prize_name: str | None) -> VKMessageText:
    title = f"🎁 {prize_name}" if prize_name else "🎁 Магазин призов"
    return VKMessageText(
        text=(
            f"{title}\n\n"
            "Получение призов пока не подключено.\n"
            "Каталог уже можно смотреть, баллы не списываются."
        ),
    )


def build_quiz_offer_message(*, task_name: str, points: int) -> VKMessageText:
    return _template_message("quiz_offer", task_name=task_name, points=points)


def build_quiz_question_message(
    *,
    question_text: str,
    question_number: int,
    total_questions: int,
) -> VKMessageText:
    return _template_message(
        "quiz_question",
        question_text=question_text,
        question_number=question_number,
        total_questions=total_questions,
    )


def build_quiz_answer_result_message(
    *,
    is_correct: bool,
    correct_option_text: str | None,
) -> VKMessageText:
    if is_correct:
        return _template_message("quiz_answer_correct")
    correct_hint = f"\nПравильный ответ: {correct_option_text}" if correct_option_text else ""
    return _template_message("quiz_answer_incorrect", correct_hint=correct_hint)


def build_quiz_unavailable_message() -> VKMessageText:
    return _template_message("quiz_unavailable")


def build_quiz_completed_message(
    *,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return _template_message(
        "quiz_completed",
        points_awarded=points_awarded,
        balance_points=balance_points,
    )


def build_quiz_failed_message() -> VKMessageText:
    return _template_message("quiz_failed")


def build_referral_link_message(*, vk_user_id: int, group_id: int) -> VKMessageText:
    return _template_message(
        "referral_link",
        link=f"https://vk.com/write-{group_id}?ref={vk_user_id}",
    )


def build_referral_bonus_message(
    *,
    bonus_points: int,
    balance_points: int,
) -> VKMessageText:
    return _template_message(
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
    return _template_message(
        "referral_milestone",
        milestone_count=milestone_count,
        bonus_points=bonus_points,
        balance_points=balance_points,
    )


def build_week_completion_reward_message(
    *,
    week_number: int,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return _template_message(
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
    return _template_message(
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
    return _template_message(
        "monthly_top_reward",
        rank=rank,
        points_awarded=points_awarded,
        balance_points=balance_points,
    )


def build_level_up_message(*, new_level: int, level_name: str, balance_points: int) -> VKMessageText:
    return _template_message(
        "level_up",
        new_level=new_level,
        level_name=level_name,
        balance_points=balance_points,
    )


def _build_greeting(*, first_name: str | None) -> str:
    clean_first_name = first_name.strip() if first_name is not None else ""
    if clean_first_name:
        return f"Привет, {clean_first_name}!"
    return "Привет!"


def _build_store_catalog_prize_line(*, index: int, prize: StorePrizeView) -> str:
    return (
        f"{index}. {prize.prize_name}\n"
        f"{prize.cost_points} ✦ · {_format_store_prize_state(prize)}"
    )


def _format_store_prize_state(prize: StorePrizeView) -> str:
    if prize.user_state == StorePrizeUserState.AVAILABLE:
        return "доступен"
    if prize.user_state == StorePrizeUserState.INSUFFICIENT_BALANCE:
        return f"не хватает {prize.missing_points} ✦"
    if prize.user_state == StorePrizeUserState.LEVEL_LOCKED:
        required_level = prize.required_level if prize.required_level is not None else "выше"
        return f"нужен уровень {required_level}"
    return "разобрали"


def _format_prize_quantity(prize: StorePrizeView) -> str:
    if prize.user_state == StorePrizeUserState.SOLD_OUT:
        return "разобрали"
    if prize.quantity_total is None:
        return "без ограничения"
    return f"{prize.quantity_remaining} из {prize.quantity_total}"


def _format_prize_type(prize_type: PrizeType) -> str:
    if prize_type == PrizeType.MERCH:
        return "Мерч"
    if prize_type == PrizeType.PARTNER:
        return "Партнёрский приз"
    if prize_type == PrizeType.SUPER_PRIZE:
        return "Суперприз"
    return "Приз"


def _format_optional_description(description: str | None) -> str:
    clean_description = description.strip() if description is not None else ""
    if not clean_description:
        return ""
    return f"\n\n{clean_description}"


def _template_message(code: str, **context: object) -> VKMessageText:
    definition = get_message_template_definition(code)
    if definition is None:
        raise RuntimeError(f"Неизвестный шаблон сообщения: {code}")

    return VKMessageText(
        text=definition.default_template.format_map(context),
        template_code=code,
        template_context=context,
    )


__all__ = [
    "VKMessageText",
    "build_balance_message",
    "build_comment_reward_message",
    "build_consent_request_message",
    "build_level_up_message",
    "build_like_reward_message",
    "build_main_menu_message",
    "build_monthly_top_reward_message",
    "build_project_completion_reward_message",
    "build_quiz_answer_result_message",
    "build_quiz_completed_message",
    "build_quiz_failed_message",
    "build_quiz_offer_message",
    "build_quiz_question_message",
    "build_quiz_unavailable_message",
    "build_referral_bonus_message",
    "build_referral_link_message",
    "build_referral_milestone_message",
    "build_registration_welcome_message",
    "build_repost_reward_message",
    "build_store_catalog_message",
    "build_store_catalog_carousel_message",
    "build_store_catalog_navigation_message",
    "build_store_claim_unavailable_message",
    "build_store_exit_message",
    "build_store_prize_card_message",
    "build_store_prize_not_found_message",
    "build_store_root_message",
    "build_subscription_reward_message",
    "build_task_accrual_message",
    "build_task_info_message",
    "build_tasks_message",
    "build_tasks_carousel_message",
    "build_week_completion_reward_message",
]
