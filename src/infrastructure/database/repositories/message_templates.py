from sqlalchemy import select
from sqlmodel import col

from application.common.dto.message_template import MessageTemplateRecord
from application.interface.repositories.message_templates import IMessageTemplateRepository
from infrastructure.database.models.message_templates import MessageTemplate
from infrastructure.database.repositories.base import SQLAlchemyRepository


class MessageTemplateRepository(SQLAlchemyRepository, IMessageTemplateRepository):
    async def get_by_code(self, code: str) -> MessageTemplateRecord | None:
        result = await self._session.execute(
            select(MessageTemplate).where(col(MessageTemplate.code) == code),
        )
        template = result.scalar_one_or_none()
        if template is None:
            return None
        return self._to_record(template)

    async def list_all(self) -> tuple[MessageTemplateRecord, ...]:
        result = await self._session.execute(
            select(MessageTemplate).order_by(col(MessageTemplate.code)),
        )
        return tuple(self._to_record(template) for template in result.scalars().all())

    async def upsert(
        self,
        *,
        code: str,
        template_text: str,
    ) -> MessageTemplateRecord:
        result = await self._session.execute(
            select(MessageTemplate).where(col(MessageTemplate.code) == code),
        )
        template = result.scalar_one_or_none()
        if template is None:
            template = MessageTemplate(code=code, template_text=template_text)
            self._session.add(template)
        else:
            template.template_text = template_text

        await self._session.flush()
        return self._to_record(template)

    async def delete_by_code(self, *, code: str) -> bool:
        result = await self._session.execute(
            select(MessageTemplate).where(col(MessageTemplate.code) == code),
        )
        template = result.scalar_one_or_none()
        if template is None:
            return False

        await self._session.delete(template)
        await self._session.flush()
        return True

    @staticmethod
    def _to_record(template: MessageTemplate) -> MessageTemplateRecord:
        return MessageTemplateRecord(
            code=template.code,
            template_text=template.template_text,
        )
