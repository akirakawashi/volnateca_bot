from abc import ABC, abstractmethod

from application.common.dto.message_template import MessageTemplateRecord


class IMessageTemplateRepository(ABC):
    @abstractmethod
    async def get_by_code(self, code: str) -> MessageTemplateRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> tuple[MessageTemplateRecord, ...]:
        raise NotImplementedError

    @abstractmethod
    async def upsert(
        self,
        *,
        code: str,
        template_text: str,
    ) -> MessageTemplateRecord:
        raise NotImplementedError

    @abstractmethod
    async def delete_by_code(self, *, code: str) -> bool:
        raise NotImplementedError


__all__ = ["IMessageTemplateRepository"]
