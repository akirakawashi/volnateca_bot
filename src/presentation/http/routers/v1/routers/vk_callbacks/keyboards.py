import json

VKKeyboard = dict[str, object]


def build_main_menu_keyboard() -> VKKeyboard:
    return {
        "one_time": False,
        "buttons": [
            [
                _text_button(label="💫 Баланс", color="primary"),
                _text_button(label="🎯 Задания", color="primary"),
            ],
            [
                _text_button(label="🎁 Магазин", color="secondary"),
                _text_button(label="🤝 Рефералка", color="secondary"),
            ],
        ],
    }


def build_quiz_offer_keyboard(tasks_id: int) -> VKKeyboard:
    return {
        "one_time": True,
        "buttons": [
            [
                _payload_button(
                    label="✅ Участвовать",
                    color="positive",
                    payload={"action": "start_quiz", "tasks_id": tasks_id},
                ),
                _payload_button(
                    label="❌ Пропустить",
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
            _payload_button(
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


def _text_button(*, label: str, color: str) -> dict[str, object]:
    return {
        "action": {
            "type": "text",
            "label": label,
        },
        "color": color,
    }


def _payload_button(*, label: str, color: str, payload: dict) -> dict[str, object]:
    return {
        "action": {
            "type": "text",
            "label": label,
            "payload": json.dumps(payload, ensure_ascii=False),
        },
        "color": color,
    }


__all__ = [
    "VKKeyboard",
    "build_main_menu_keyboard",
    "build_quiz_offer_keyboard",
    "build_quiz_question_keyboard",
]
