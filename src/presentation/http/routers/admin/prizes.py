from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, status

from application.admin.command.create_prize import CreatePrizeHandler
from application.admin.command.list_prizes import ListPrizesHandler
from application.admin.dto.prize import ListPrizesCommand
from presentation.http.dto.admin.prize import CreatePrizeRequestSchema, PrizeResponseSchema

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
