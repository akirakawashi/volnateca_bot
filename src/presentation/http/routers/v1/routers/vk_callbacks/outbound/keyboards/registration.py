from presentation.http.routers.v1.routers.vk_callbacks.outbound.keyboards.buttons import (
    VKKeyboard,
    payload_button,
)


def build_consent_keyboard(*, ref_key: str | None = None) -> VKKeyboard:
    accept_payload: dict[str, object] = {"action": "consent_accept"}
    clean_ref_key = ref_key.strip() if ref_key is not None else ""
    if clean_ref_key:
        accept_payload["consent_ref"] = clean_ref_key

    return {
        "one_time": True,
        "buttons": [
            [
                payload_button(label="Да", color="positive", payload=accept_payload),
                payload_button(
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
        "buttons": build_main_menu_rows(),
    }


def build_main_menu_rows() -> list[list[dict[str, object]]]:
    return [
        [
            payload_button(label="💫 Баланс", color="primary", payload={"action": "balance"}),
            payload_button(label="🎯 Задания", color="primary", payload={"action": "tasks"}),
        ],
        [
            payload_button(label="🎁 Магазин", color="secondary", payload={"action": "shop"}),
            payload_button(label="🤝 Пригласить друга", color="secondary", payload={"action": "referral"}),
        ],
    ]
