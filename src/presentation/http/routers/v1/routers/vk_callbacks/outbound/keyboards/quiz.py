from presentation.http.routers.v1.routers.vk_callbacks.outbound.keyboards.buttons import (
    VKKeyboard,
    payload_button,
)


def build_quiz_offer_keyboard(tasks_id: int) -> VKKeyboard:
    return {
        "one_time": True,
        "buttons": [
            [
                payload_button(
                    label="✅ Участвовать",
                    color="positive",
                    payload={"action": "start_quiz", "tasks_id": tasks_id},
                ),
            ],
            [
                payload_button(
                    label="❌ Сделаю позже, показать задания",
                    color="secondary",
                    payload={"action": "skip_quiz"},
                ),
            ],
        ],
    }


def build_quiz_question_keyboard(
    quiz_questions_id: int,
    options: list[tuple[int, str]],
) -> VKKeyboard:
    """Клавиатура с вариантами ответов на вопрос квиза.

    Args:
        quiz_questions_id: ID вопроса.
        options: список пар (quiz_question_options_id, option_text).
    """
    buttons = [
        [
            payload_button(
                label=option_text[:40],
                color="secondary",
                payload={
                    "action": "quiz_answer",
                    "quiz_questions_id": quiz_questions_id,
                    "option_id": option_id,
                },
            )
        ]
        for option_id, option_text in options
    ]
    return {"one_time": True, "buttons": buttons}
