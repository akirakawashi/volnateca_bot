from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, status

from application.admin.command.message_templates import (
    DeleteMessageTemplateCommand,
    DeleteMessageTemplateHandler,
    ListMessageTemplatesCommand,
    ListMessageTemplatesHandler,
    UpsertMessageTemplateCommand,
    UpsertMessageTemplateHandler,
)
from presentation.http.dto.admin.message_templates import (
    MessageTemplateResponseSchema,
    MessageTemplateUpsertRequestSchema,
)

message_templates_admin_router = APIRouter(route_class=DishkaRoute)


@message_templates_admin_router.get(
    path="/message-templates",
    name="Получить список шаблонов сообщений",
    response_model=list[MessageTemplateResponseSchema],
    status_code=200,
)
async def list_message_templates(
    handler: FromDishka[ListMessageTemplatesHandler],
) -> list[MessageTemplateResponseSchema]:
    result = await handler(ListMessageTemplatesCommand())
    return [MessageTemplateResponseSchema.from_dto(item) for item in result]


@message_templates_admin_router.put(
    path="/message-templates/{code}",
    name="Обновить шаблон сообщения",
    response_model=MessageTemplateResponseSchema,
    status_code=200,
)
async def upsert_message_template(
    code: str,
    data: MessageTemplateUpsertRequestSchema,
    handler: FromDishka[UpsertMessageTemplateHandler],
) -> MessageTemplateResponseSchema:
    try:
        result = await handler(
            UpsertMessageTemplateCommand(code=code, template_text=data.template_text),
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.args[0]) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return MessageTemplateResponseSchema.from_dto(result)


@message_templates_admin_router.delete(
    path="/message-templates/{code}",
    name="Сбросить шаблон сообщения к дефолту",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_message_template(
    code: str,
    handler: FromDishka[DeleteMessageTemplateHandler],
) -> None:
    try:
        await handler(DeleteMessageTemplateCommand(code=code))
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.args[0]) from exc
