from dataclasses import dataclass, field

from application.services.vk_message_template_catalog import get_message_template_definition


@dataclass(slots=True, frozen=True, kw_only=True)
class VKMessageText:
    text: str
    template_code: str | None = None
    template_context: dict[str, object] = field(default_factory=dict)


def build_greeting(*, first_name: str | None) -> str:
    clean_first_name = first_name.strip() if first_name is not None else ""
    if clean_first_name:
        return f"Привет, {clean_first_name}!"
    return "Привет!"


def build_template_message(code: str, **context: object) -> VKMessageText:
    definition = get_message_template_definition(code)
    if definition is None:
        raise RuntimeError(f"Неизвестный шаблон сообщения: {code}")

    return VKMessageText(
        text=definition.default_template.format_map(context),
        template_code=code,
        template_context=context,
    )
