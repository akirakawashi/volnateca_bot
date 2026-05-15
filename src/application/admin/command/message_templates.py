from dataclasses import dataclass

from application.base_interactor import Interactor
from application.common.dto.message_template import MessageTemplateDTO
from application.interface.services import IVKMessageTemplateService
from application.interface.uow import IUnitOfWork


@dataclass(slots=True, frozen=True, kw_only=True)
class ListMessageTemplatesCommand:
    pass


@dataclass(slots=True, frozen=True, kw_only=True)
class UpsertMessageTemplateCommand:
    code: str
    template_text: str


@dataclass(slots=True, frozen=True, kw_only=True)
class DeleteMessageTemplateCommand:
    code: str


class ListMessageTemplatesHandler(
    Interactor[ListMessageTemplatesCommand, tuple[MessageTemplateDTO, ...]],
):
    def __init__(self, service: IVKMessageTemplateService) -> None:
        self._service = service

    async def __call__(
        self,
        command_data: ListMessageTemplatesCommand,
    ) -> tuple[MessageTemplateDTO, ...]:
        return await self._service.list_templates()


class UpsertMessageTemplateHandler(Interactor[UpsertMessageTemplateCommand, MessageTemplateDTO]):
    def __init__(
        self,
        service: IVKMessageTemplateService,
        uow: IUnitOfWork,
    ) -> None:
        self._service = service
        self._uow = uow

    async def __call__(self, command_data: UpsertMessageTemplateCommand) -> MessageTemplateDTO:
        result = await self._service.upsert_template(
            code=command_data.code,
            template_text=command_data.template_text,
        )
        await self._uow.commit()
        return result


class DeleteMessageTemplateHandler(Interactor[DeleteMessageTemplateCommand, None]):
    def __init__(
        self,
        service: IVKMessageTemplateService,
        uow: IUnitOfWork,
    ) -> None:
        self._service = service
        self._uow = uow

    async def __call__(self, command_data: DeleteMessageTemplateCommand) -> None:
        await self._service.delete_template_override(code=command_data.code)
        await self._uow.commit()
