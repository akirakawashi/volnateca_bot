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


def _text_button(*, label: str, color: str) -> dict[str, object]:
    return {
        "action": {
            "type": "text",
            "label": label,
        },
        "color": color,
    }


__all__ = ["VKKeyboard", "build_main_menu_keyboard"]
