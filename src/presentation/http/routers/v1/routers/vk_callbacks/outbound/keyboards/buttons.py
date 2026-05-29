import json

VKKeyboard = dict[str, object]
VKTemplate = dict[str, object]


def payload_button(*, label: str, color: str, payload: dict) -> dict[str, object]:
    return {
        "action": {
            "type": "text",
            "label": label,
            "payload": json.dumps(payload, ensure_ascii=False),
        },
        "color": color,
    }


def truncate_button_label(label: str) -> str:
    clean_label = label.strip()
    if len(clean_label) <= 40:
        return clean_label
    return f"{clean_label[:39]}…"


def truncate_carousel_text(text: str, *, max_length: int) -> str:
    clean_text = " ".join(text.split())
    if len(clean_text) <= max_length:
        return clean_text
    return f"{clean_text[: max_length - 1]}…"
