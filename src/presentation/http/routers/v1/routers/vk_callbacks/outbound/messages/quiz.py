from presentation.http.routers.v1.routers.vk_callbacks.outbound.messages._template import (
    VKMessageText,
    _template_message,
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
