import json

from application.common.dto.store import (
    StoreCatalogDTO,
    StorePrizeCardDTO,
    StorePrizeUserState,
    list_store_sections,
)

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


def build_store_root_keyboard() -> VKKeyboard:
    return {
        "one_time": False,
        "buttons": [
            [
                _payload_button(
                    label=section.label,
                    color="secondary",
                    payload={"action": "store_catalog", "section": section.value, "page": 1},
                )
                for section in list_store_sections()[:2]
            ],
            [
                _payload_button(
                    label=section.label,
                    color="secondary",
                    payload={"action": "store_catalog", "section": section.value, "page": 1},
                )
                for section in list_store_sections()[2:]
            ],
        ],
    }


def build_store_catalog_keyboard(catalog: StoreCatalogDTO) -> VKKeyboard:
    buttons: list[list[dict[str, object]]] = [
        [
            _payload_button(
                label=_truncate_button_label(
                    f"{_store_state_icon(prize.user_state)} {prize.prize_name} · {prize.cost_points} ✦",
                ),
                color="secondary",
                payload={
                    "action": "store_prize",
                    "prizes_id": prize.prizes_id,
                    "section": catalog.section.value,
                    "page": catalog.pagination.page,
                },
            ),
        ]
        for prize in catalog.prizes
    ]

    navigation_row: list[dict[str, object]] = []
    if catalog.pagination.has_previous:
        navigation_row.append(
            _payload_button(
                label="← Назад",
                color="secondary",
                payload={
                    "action": "store_catalog",
                    "section": catalog.section.value,
                    "page": catalog.pagination.page - 1,
                },
            ),
        )
    if catalog.pagination.has_next:
        navigation_row.append(
            _payload_button(
                label="Вперёд →",
                color="secondary",
                payload={
                    "action": "store_catalog",
                    "section": catalog.section.value,
                    "page": catalog.pagination.page + 1,
                },
            ),
        )
    if navigation_row:
        buttons.append(navigation_row)

    buttons.append(
        [
            _payload_button(
                label="Разделы",
                color="primary",
                payload={"action": "store_root"},
            ),
        ],
    )
    return {"one_time": False, "buttons": buttons}


def build_store_prize_card_keyboard(card: StorePrizeCardDTO) -> VKKeyboard:
    prize = card.prize
    if prize is None:
        return build_store_root_keyboard()

    return {
        "one_time": False,
        "buttons": [
            [
                _payload_button(
                    label="Получить",
                    color="positive" if prize.user_state == StorePrizeUserState.AVAILABLE else "secondary",
                    payload={
                        "action": "store_claim",
                        "prizes_id": prize.prizes_id,
                        "section": card.section.value,
                        "page": card.page,
                    },
                ),
            ],
            [
                _payload_button(
                    label="Назад в каталог",
                    color="primary",
                    payload={
                        "action": "store_catalog",
                        "section": card.section.value,
                        "page": card.page,
                    },
                ),
            ],
        ],
    }


def build_store_prize_not_found_keyboard() -> VKKeyboard:
    return build_store_root_keyboard()


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


def _store_state_icon(state: StorePrizeUserState) -> str:
    if state == StorePrizeUserState.AVAILABLE:
        return "✅"
    if state == StorePrizeUserState.INSUFFICIENT_BALANCE:
        return "💫"
    if state == StorePrizeUserState.LEVEL_LOCKED:
        return "🔒"
    return "⏳"


def _truncate_button_label(label: str) -> str:
    clean_label = label.strip()
    if len(clean_label) <= 40:
        return clean_label
    return f"{clean_label[:39]}…"


__all__ = [
    "VKKeyboard",
    "build_main_menu_keyboard",
    "build_quiz_offer_keyboard",
    "build_quiz_question_keyboard",
    "build_store_catalog_keyboard",
    "build_store_prize_card_keyboard",
    "build_store_prize_not_found_keyboard",
    "build_store_root_keyboard",
]
