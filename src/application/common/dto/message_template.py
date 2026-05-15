from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class MessageTemplateRecord:
    code: str
    template_text: str


@dataclass(slots=True, frozen=True, kw_only=True)
class MessageTemplateDTO:
    code: str
    description: str
    variables: tuple[str, ...]
    default_template: str
    override_template: str | None
    effective_template: str


__all__ = ["MessageTemplateDTO", "MessageTemplateRecord"]
