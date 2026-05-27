import json

from application.common.dto.store import (
    StoreCatalogDTO,
    StorePrizeCardDTO,
    StorePrizeUserState,
    list_store_sections,
)
from utils.vk_attachments import to_vk_carousel_photo_id

VKKeyboard = dict[str, object]
VKTemplate = dict[str, object]


def build_consent_keyboard(*, ref_key: str | None = None) -> VKKeyboard:
    accept_payload: dict[str, object] = {"action": "consent_accept"}
    clean_ref_key = ref_key.strip() if ref_key is not None else ""
    if clean_ref_key:
        accept_payload["consent_ref"] = clean_ref_key

    return {
        "one_time": True,
        "buttons": [
            [
                _payload_button(label="Да", color="positive", payload=accept_payload),
                _payload_button(
                    label="Нет",
                    color="negative",
                    payload={"action": "consent_decline"},
                ),
            ],
        ],
    }


def build_main_menu_keyboard() -> VKKeyboard:
    return {
        "one_time": False,
        "buttons": [
            [
                _payload_button(label="💫 Баланс", color="primary", payload={"action": "balance"}),
                _payload_button(label="🎯 Задания", color="primary", payload={"action": "tasks"}),
            ],
            [
                _payload_button(label="🎁 Магазин", color="secondary", payload={"action": "shop"}),
                _payload_button(label="🤝 Рефералка", color="secondary", payload={"action": "referral"}),
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
            *_build_store_section_rows(),
            _build_store_exit_row(label="Главное меню"),
        ],
    }


def build_store_catalog_keyboard(
    catalog: StoreCatalogDTO,
    *,
    include_prize_buttons: bool = False,
) -> VKKeyboard:
    buttons: list[list[dict[str, object]]] = []

    if include_prize_buttons:
        buttons.extend(
            [
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
            ],
        )

    navigation_row = _build_store_catalog_navigation_row(catalog)
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


def build_store_catalog_navigation_keyboard(catalog: StoreCatalogDTO) -> VKKeyboard:
    buttons: list[list[dict[str, object]]] = []

    navigation_row = _build_store_catalog_navigation_row(catalog)
    if navigation_row:
        buttons.append(navigation_row)

    buttons.extend(_build_store_section_rows())
    buttons.append(_build_store_exit_row())
    return {"one_time": False, "buttons": buttons}


def build_store_catalog_carousel_template(catalog: StoreCatalogDTO) -> VKTemplate | None:
    if not catalog.prizes:
        return None

    elements: list[dict[str, object]] = []
    for prize in catalog.prizes:
        photo_id = to_vk_carousel_photo_id(prize.image_attachment)
        if photo_id is None:
            return None

        elements.append(
            {
                "title": _truncate_carousel_text(prize.prize_name, max_length=80),
                "description": _truncate_carousel_text(
                    f"{prize.cost_points} ✦ · {_format_store_carousel_state(prize.user_state)}",
                    max_length=80,
                ),
                "photo_id": photo_id,
                "action": {"type": "open_photo"},
                "buttons": [
                    _payload_button(
                        label="Открыть",
                        color="primary",
                        payload={
                            "action": "store_prize",
                            "prizes_id": prize.prizes_id,
                            "section": catalog.section.value,
                            "page": catalog.pagination.page,
                        },
                    ),
                ],
            },
        )

    return {
        "type": "carousel",
        "elements": elements,
    }


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


def build_store_exit_keyboard() -> VKKeyboard:
    return build_main_menu_keyboard()


def _build_store_catalog_navigation_row(catalog: StoreCatalogDTO) -> list[dict[str, object]]:
    buttons: list[dict[str, object]] = []
    if catalog.pagination.has_previous:
        buttons.append(
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
        buttons.append(
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
    return buttons


def _build_store_section_rows() -> list[list[dict[str, object]]]:
    sections = list_store_sections()
    return [
        [
            _payload_button(
                label=section.label,
                color="secondary",
                payload={"action": "store_catalog", "section": section.value, "page": 1},
            )
            for section in sections[:2]
        ],
        [
            _payload_button(
                label=section.label,
                color="secondary",
                payload={"action": "store_catalog", "section": section.value, "page": 1},
            )
            for section in sections[2:]
        ],
    ]


def _build_store_exit_row(*, label: str = "Выйти из магазина") -> list[dict[str, object]]:
    return [
        _payload_button(
            label=label,
            color="primary",
            payload={"action": "store_exit"},
        ),
    ]


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


def _truncate_carousel_text(text: str, *, max_length: int) -> str:
    clean_text = " ".join(text.split())
    if len(clean_text) <= max_length:
        return clean_text
    return f"{clean_text[: max_length - 1]}…"


def _format_store_carousel_state(state: StorePrizeUserState) -> str:
    if state == StorePrizeUserState.AVAILABLE:
        return "доступен"
    if state == StorePrizeUserState.INSUFFICIENT_BALANCE:
        return "не хватает баллов"
    if state == StorePrizeUserState.LEVEL_LOCKED:
        return "закрыт по уровню"
    return "разобрали"


__all__ = [
    "VKKeyboard",
    "VKTemplate",
    "build_consent_keyboard",
    "build_main_menu_keyboard",
    "build_quiz_offer_keyboard",
    "build_quiz_question_keyboard",
    "build_store_catalog_carousel_template",
    "build_store_catalog_keyboard",
    "build_store_catalog_navigation_keyboard",
    "build_store_exit_keyboard",
    "build_store_prize_card_keyboard",
    "build_store_prize_not_found_keyboard",
    "build_store_root_keyboard",
]
