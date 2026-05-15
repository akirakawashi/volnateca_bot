from dataclasses import dataclass, field

from application.common.dto.task import VKUserAvailableTaskDTO
from application.services.vk_message_template_catalog import get_message_template_definition


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


def build_help_message() -> VKMessageText:
    return _template_message("help")


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


def build_free_text_fallback_message() -> VKMessageText:
    return _template_message("free_text_fallback")


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


def build_daily_streak_reward_message(
    *,
    streak_days: int,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return _template_message(
        "daily_streak_reward",
        streak_days=streak_days,
        points_awarded=points_awarded,
        balance_points=balance_points,
    )


def build_quiz_streak_reward_message(
    *,
    streak_count: int,
    points_awarded: int,
    balance_points: int,
) -> VKMessageText:
    return _template_message(
        "quiz_streak_reward",
        streak_count=streak_count,
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
    "build_daily_streak_reward_message",
    "build_free_text_fallback_message",
    "build_help_message",
    "build_level_up_message",
    "build_like_reward_message",
    "build_monthly_top_reward_message",
    "build_project_completion_reward_message",
    "build_quiz_answer_result_message",
    "build_quiz_completed_message",
    "build_quiz_offer_message",
    "build_quiz_question_message",
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
