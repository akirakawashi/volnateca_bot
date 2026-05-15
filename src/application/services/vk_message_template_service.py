import string
from collections.abc import Mapping

from application.common.dto.message_template import MessageTemplateDTO
from application.interface.repositories.message_templates import IMessageTemplateRepository
from application.interface.services.message_templates import IVKMessageTemplateService
from application.services.vk_message_template_catalog import (
    get_message_template_definition,
    list_message_template_definitions,
)


class VKMessageTemplateService(IVKMessageTemplateService):
    def __init__(self, repository: IMessageTemplateRepository) -> None:
        self._repository = repository
        self._override_cache: dict[str, str | None] = {}

    async def render(
        self,
        *,
        code: str | None,
        fallback_text: str,
        context: Mapping[str, object] | None = None,
    ) -> str:
        if code is None:
            return fallback_text

        definition = get_message_template_definition(code)
        if definition is None:
            return fallback_text

        override_text = await self._get_override_text(code)
        if override_text is None:
            return fallback_text

        try:
            return override_text.format_map(dict(context or {}))
        except (KeyError, ValueError, IndexError):
            return fallback_text

    async def list_templates(self) -> tuple[MessageTemplateDTO, ...]:
        overrides = {item.code: item.template_text for item in await self._repository.list_all()}
        return tuple(
            MessageTemplateDTO(
                code=definition.code,
                description=definition.description,
                variables=definition.variables,
                default_template=definition.default_template,
                override_template=overrides.get(definition.code),
                effective_template=overrides.get(definition.code, definition.default_template),
            )
            for definition in list_message_template_definitions()
        )

    async def upsert_template(
        self,
        *,
        code: str,
        template_text: str,
    ) -> MessageTemplateDTO:
        definition = self._require_definition(code)
        self._validate_template(definition.variables, template_text)

        record = await self._repository.upsert(code=code, template_text=template_text)
        self._override_cache[code] = record.template_text
        return MessageTemplateDTO(
            code=definition.code,
            description=definition.description,
            variables=definition.variables,
            default_template=definition.default_template,
            override_template=record.template_text,
            effective_template=record.template_text,
        )

    async def delete_template_override(self, *, code: str) -> bool:
        self._require_definition(code)
        deleted = await self._repository.delete_by_code(code=code)
        self._override_cache[code] = None
        return deleted

    async def _get_override_text(self, code: str) -> str | None:
        if code in self._override_cache:
            return self._override_cache[code]

        record = await self._repository.get_by_code(code)
        override_text = record.template_text if record is not None else None
        self._override_cache[code] = override_text
        return override_text

    @staticmethod
    def _validate_template(allowed_variables: tuple[str, ...], template_text: str) -> None:
        allowed = set(allowed_variables)

        try:
            parsed = tuple(string.Formatter().parse(template_text))
        except ValueError as exc:
            raise ValueError("Некорректный синтаксис шаблона") from exc

        for _, field_name, _, _ in parsed:
            if field_name is None:
                continue
            if field_name == "":
                raise ValueError("Позиционные placeholders не поддерживаются")
            if any(marker in field_name for marker in (".", "[", "]")):
                raise ValueError("Вложенные placeholders не поддерживаются")
            if field_name not in allowed:
                available = ", ".join(allowed_variables) if allowed_variables else "нет"
                raise ValueError(
                    f"Неизвестный placeholder '{field_name}'. Доступны: {available}",
                )

    @staticmethod
    def _require_definition(code: str):
        definition = get_message_template_definition(code)
        if definition is None:
            raise KeyError(f"Шаблон сообщения '{code}' не поддерживается")
        return definition
