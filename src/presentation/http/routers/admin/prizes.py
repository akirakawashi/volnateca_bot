from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, status

from application.admin.command.create_prize import CreatePrizeHandler
from application.admin.command.list_prizes import ListPrizesHandler
from application.admin.command.update_prize import UpdatePrizeHandler
from application.admin.dto.prize import ListPrizesCommand
from presentation.http.dto.admin.prize import (
    CreatePrizeRequestSchema,
    PrizeResponseSchema,
    UpdatePrizeRequestSchema,
)

prizes_admin_router = APIRouter(route_class=DishkaRoute)


@prizes_admin_router.get(
    path="/prizes",
    name="Получить список призов",
    response_model=list[PrizeResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def list_prizes(
    handler: FromDishka[ListPrizesHandler],
) -> list[PrizeResponseSchema]:
    result = await handler(ListPrizesCommand())
    return [PrizeResponseSchema.from_dto(item) for item in result]


@prizes_admin_router.post(
    path="/prizes",
    name="Создать приз",
    response_model=PrizeResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_prize(
    data: CreatePrizeRequestSchema,
    handler: FromDishka[CreatePrizeHandler],
) -> PrizeResponseSchema:
    try:
        result = await handler(data.to_command())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return PrizeResponseSchema.from_dto(result)


@prizes_admin_router.patch(
    path="/prizes/{prizes_id}",
    name="Обновить приз",
    response_model=PrizeResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_prize(
    prizes_id: int,
    data: UpdatePrizeRequestSchema,
    handler: FromDishka[UpdatePrizeHandler],
) -> PrizeResponseSchema:
    try:
        result = await handler(data.to_command(prizes_id=prizes_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Приз не найден")
    return PrizeResponseSchema.from_dto(result)
