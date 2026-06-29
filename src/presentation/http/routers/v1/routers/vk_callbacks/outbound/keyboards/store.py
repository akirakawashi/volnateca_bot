from application.common.dto.store import (
    StoreCatalogDTO,
    StorePrizeCardDTO,
    StorePrizeUserState,
    StoreSection,
)
from presentation.http.routers.v1.routers.vk_callbacks.outbound.keyboards.buttons import (
    VKKeyboard,
    VKTemplate,
    payload_button,
    truncate_button_label,
    truncate_carousel_text,
)
from presentation.http.routers.v1.routers.vk_callbacks.outbound.keyboards.registration import (
    build_main_menu_keyboard,
)
from utils.vk_attachments import to_vk_carousel_photo_id


def build_store_root_keyboard() -> VKKeyboard:
    return {
        "one_time": False,
        "buttons": [
            [
                payload_button(
                    label="Посмотреть призы",
                    color="primary",
                    payload={
                        "action": "store_catalog",
                        "section": StoreSection.ALL.value,
                        "page": 1,
                    },
                ),
            ],
            [
                payload_button(
                    label="📦 Мои призы",
                    color="secondary",
                    payload={"action": "store_my_redemptions", "page": 1},
                ),
            ],
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
                    payload_button(
                        label=truncate_button_label(
                            f"{_store_state_icon(prize.user_state)} {prize.prize_name} · {prize.cost_points} ✦".strip(),
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

    buttons.extend(_build_store_catalog_service_rows())
    return {"one_time": False, "buttons": buttons}


def build_store_catalog_navigation_keyboard(catalog: StoreCatalogDTO) -> VKKeyboard:
    buttons: list[list[dict[str, object]]] = []

    navigation_row = _build_store_catalog_navigation_row(catalog)
    if navigation_row:
        buttons.append(navigation_row)

    buttons.extend(_build_store_catalog_service_rows())
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
                "title": truncate_carousel_text(prize.prize_name, max_length=80),
                "description": truncate_carousel_text(
                    f"{prize.cost_points} ✦ · {_format_store_carousel_state(prize.user_state)}",
                    max_length=80,
                ),
                "photo_id": photo_id,
                "action": {"type": "open_photo"},
                "buttons": [
                    payload_button(
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

    buttons: list[list[dict[str, object]]] = []
    if prize.user_state == StorePrizeUserState.AVAILABLE:
        buttons.append(
            [
                payload_button(
                    label="Получить",
                    color="positive",
                    payload={
                        "action": "store_claim",
                        "prizes_id": prize.prizes_id,
                        "section": card.section.value,
                        "page": card.page,
                    },
                ),
            ],
        )

    return {
        "one_time": False,
        "buttons": [
            *buttons,
            [
                payload_button(
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


def build_store_claim_confirm_keyboard(
    *,
    prizes_id: int,
    section: str,
    page: int,
    idempotency_key: str,
) -> VKKeyboard:
    return {
        "one_time": False,
        "buttons": [
            [
                payload_button(
                    label="Подтвердить",
                    color="positive",
                    payload={
                        "action": "store_claim_confirm",
                        "prizes_id": prizes_id,
                        "section": section,
                        "page": page,
                        "idempotency_key": idempotency_key,
                    },
                ),
            ],
            [
                payload_button(
                    label="Назад",
                    color="secondary",
                    payload={
                        "action": "store_prize",
                        "prizes_id": prizes_id,
                        "section": section,
                        "page": page,
                    },
                ),
            ],
        ],
    }


def build_store_my_redemptions_keyboard(*, page: int, has_previous: bool, has_next: bool) -> VKKeyboard:
    buttons: list[list[dict[str, object]]] = []
    navigation: list[dict[str, object]] = []
    if has_previous:
        navigation.append(
            payload_button(
                label="← Назад",
                color="secondary",
                payload={"action": "store_my_redemptions", "page": page - 1},
            ),
        )
    if has_next:
        navigation.append(
            payload_button(
                label="Вперёд →",
                color="secondary",
                payload={"action": "store_my_redemptions", "page": page + 1},
            ),
        )
    if navigation:
        buttons.append(navigation)
    buttons.append(
        [
            payload_button(
                label="В магазин",
                color="primary",
                payload={"action": "store_root"},
            ),
        ],
    )
    buttons.append(_build_store_exit_row(label="Главное меню"))
    return {"one_time": False, "buttons": buttons}


def build_store_redeem_result_keyboard(
    *,
    section: str,
    page: int,
) -> VKKeyboard:
    return {
        "one_time": False,
        "buttons": [
            [
                payload_button(
                    label="📦 Мои призы",
                    color="secondary",
                    payload={"action": "store_my_redemptions", "page": 1},
                ),
            ],
            [
                payload_button(
                    label="В каталог",
                    color="primary",
                    payload={"action": "store_catalog", "section": section, "page": page},
                ),
            ],
            _build_store_exit_row(label="Главное меню"),
        ],
    }


def _build_store_catalog_navigation_row(catalog: StoreCatalogDTO) -> list[dict[str, object]]:
    buttons: list[dict[str, object]] = []
    if catalog.pagination.has_previous:
        buttons.append(
            payload_button(
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
            payload_button(
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


def _build_store_catalog_service_rows() -> list[list[dict[str, object]]]:
    return [
        [
            payload_button(
                label="📦 Мои призы",
                color="secondary",
                payload={"action": "store_my_redemptions", "page": 1},
            )
        ],
        [
            payload_button(
                label="В магазин",
                color="primary",
                payload={"action": "store_root"},
            )
        ],
        _build_store_exit_row(label="Главное меню"),
    ]


def _build_store_exit_row(*, label: str = "Выйти из магазина") -> list[dict[str, object]]:
    return [
        payload_button(
            label=label,
            color="primary",
            payload={"action": "store_exit"},
        ),
    ]


def _store_state_icon(state: StorePrizeUserState) -> str:
    if state == StorePrizeUserState.AVAILABLE:
        return "✅"
    if state == StorePrizeUserState.INSUFFICIENT_BALANCE:
        return ""
    if state == StorePrizeUserState.LEVEL_LOCKED:
        return "🔒"
    return "⏳"


def _format_store_carousel_state(state: StorePrizeUserState) -> str:
    if state == StorePrizeUserState.AVAILABLE:
        return "доступен"
    if state == StorePrizeUserState.INSUFFICIENT_BALANCE:
        return "не хватает баллов"
    if state == StorePrizeUserState.LEVEL_LOCKED:
        return "закрыт по уровню"
    return "разобрали"
