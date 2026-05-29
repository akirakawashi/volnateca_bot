from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, status

from application.admin.command.broadcast import (
    GetBroadcastStatusCommand,
    GetBroadcastStatusHandler,
    StartBroadcastCommand,
    StartBroadcastHandler,
)
from application.admin.services import BroadcastAlreadyRunningError, BroadcastNotFoundError
from presentation.http.dto.admin.broadcast import (
    BroadcastStartRequestSchema,
    BroadcastStartResponseSchema,
    BroadcastStatusResponseSchema,
)

broadcast_admin_router = APIRouter(route_class=DishkaRoute)


@broadcast_admin_router.post(
    path="/broadcasts",
    name="Запустить VK-рассылку",
    response_model=BroadcastStartResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_broadcast(
    data: BroadcastStartRequestSchema,
    handler: FromDishka[StartBroadcastHandler],
) -> BroadcastStartResponseSchema:
    try:
        result = await handler(StartBroadcastCommand(message=data.message))
    except BroadcastAlreadyRunningError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="VK-рассылка уже выполняется",
        ) from exc
    return BroadcastStartResponseSchema.from_dto(result)


@broadcast_admin_router.get(
    path="/broadcasts/{broadcast_id}",
    name="Получить статус VK-рассылки",
    response_model=BroadcastStatusResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_broadcast_status(
    broadcast_id: str,
    handler: FromDishka[GetBroadcastStatusHandler],
) -> BroadcastStatusResponseSchema:
    try:
        result = await handler(GetBroadcastStatusCommand(broadcast_id=broadcast_id))
    except BroadcastNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VK-рассылка не найдена",
        ) from exc
    return BroadcastStatusResponseSchema.from_dto(result)
