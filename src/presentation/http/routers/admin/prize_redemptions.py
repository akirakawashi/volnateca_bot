from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, status

from application.admin.command.prize_redemption import (
    CancelPrizeRedemptionHandler,
    FulfillPrizeRedemptionHandler,
    GetPrizeRedemptionCommand,
    GetPrizeRedemptionHandler,
    ListPrizeRedemptionsHandler,
)
from application.services.cancel_redemption_service import CancelRedemptionOutcomeStatus
from application.services.fulfill_redemption_service import FulfillRedemptionOutcomeStatus
from domain.enums.prize import PrizeRedemptionStatus
from presentation.http.dto.admin.prize_redemption import (
    CancelPrizeRedemptionRequestSchema,
    FulfillPrizeRedemptionRequestSchema,
    ListPrizeRedemptionsQuerySchema,
    PrizeRedemptionResponseSchema,
    PrizeRedemptionsPageResponseSchema,
)

prize_redemptions_admin_router = APIRouter(route_class=DishkaRoute)


@prize_redemptions_admin_router.get(
    path="/prize-redemptions",
    name="Список заявок на призы",
    response_model=PrizeRedemptionsPageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def list_prize_redemptions(
    handler: FromDishka[ListPrizeRedemptionsHandler],
    status: PrizeRedemptionStatus | None = None,
    prizes_id: int | None = None,
    page: int = 1,
) -> PrizeRedemptionsPageResponseSchema:
    result = await handler(
        ListPrizeRedemptionsQuerySchema(
            status=status,
            prizes_id=prizes_id,
            page=page,
        ).to_command(),
    )
    return PrizeRedemptionsPageResponseSchema.from_page_dto(result)


@prize_redemptions_admin_router.get(
    path="/prize-redemptions/{prize_redemptions_id}",
    name="Заявка на приз",
    response_model=PrizeRedemptionResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_prize_redemption(
    prize_redemptions_id: int,
    handler: FromDishka[GetPrizeRedemptionHandler],
) -> PrizeRedemptionResponseSchema:
    result = await handler(GetPrizeRedemptionCommand(prize_redemptions_id=prize_redemptions_id))
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заявка не найдена")
    return PrizeRedemptionResponseSchema.from_dto(result)


@prize_redemptions_admin_router.post(
    path="/prize-redemptions/{prize_redemptions_id}/fulfill",
    name="Выдать приз по заявке",
    response_model=PrizeRedemptionResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def fulfill_prize_redemption(
    prize_redemptions_id: int,
    data: FulfillPrizeRedemptionRequestSchema,
    fulfill_handler: FromDishka[FulfillPrizeRedemptionHandler],
    get_handler: FromDishka[GetPrizeRedemptionHandler],
) -> PrizeRedemptionResponseSchema:
    outcome = await fulfill_handler(data.to_command(prize_redemptions_id=prize_redemptions_id))
    if outcome.status == FulfillRedemptionOutcomeStatus.NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заявка не найдена")
    if outcome.status == FulfillRedemptionOutcomeStatus.INVALID_STATUS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Заявку можно выдать только в статусе reserved",
        )

    record = await get_handler(GetPrizeRedemptionCommand(prize_redemptions_id=prize_redemptions_id))
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заявка не найдена")
    return PrizeRedemptionResponseSchema.from_dto(record)


@prize_redemptions_admin_router.post(
    path="/prize-redemptions/{prize_redemptions_id}/cancel",
    name="Отменить заявку на приз",
    response_model=PrizeRedemptionResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def cancel_prize_redemption(
    prize_redemptions_id: int,
    data: CancelPrizeRedemptionRequestSchema,
    cancel_handler: FromDishka[CancelPrizeRedemptionHandler],
    get_handler: FromDishka[GetPrizeRedemptionHandler],
) -> PrizeRedemptionResponseSchema:
    outcome = await cancel_handler(data.to_command(prize_redemptions_id=prize_redemptions_id))
    if outcome.status == CancelRedemptionOutcomeStatus.NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заявка не найдена")
    if outcome.status == CancelRedemptionOutcomeStatus.INVALID_STATUS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Отменить можно только заявку в статусе reserved",
        )

    record = await get_handler(GetPrizeRedemptionCommand(prize_redemptions_id=prize_redemptions_id))
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заявка не найдена")
    return PrizeRedemptionResponseSchema.from_dto(record)
