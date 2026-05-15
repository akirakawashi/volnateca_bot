from abc import ABC, abstractmethod
from collections.abc import Mapping

from application.common.dto.message_template import MessageTemplateDTO


class IVKMessageTemplateService(ABC):
    @abstractmethod
    async def render(
        self,
        *,
        code: str | None,
        fallback_text: str,
        context: Mapping[str, object] | None = None,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    async def list_templates(self) -> tuple[MessageTemplateDTO, ...]:
        raise NotImplementedError

    @abstractmethod
    async def upsert_template(
        self,
        *,
        code: str,
        template_text: str,
    ) -> MessageTemplateDTO:
        raise NotImplementedError

    @abstractmethod
    async def delete_template_override(self, *, code: str) -> bool:
        raise NotImplementedError


__all__ = ["IVKMessageTemplateService"]
