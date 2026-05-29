from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, status
from loguru import logger

from application.command.award_monthly_top import (
    AwardMonthlyTopCommand,
    AwardMonthlyTopHandler,
    MonthlyTopAwardStatus,
)
from application.interface.clients import IVKMessageClient
from application.interface.services import IVKMessageTemplateService
from presentation.http.dto.admin.monthly_top import (
    AwardMonthlyTopRequestSchema,
    AwardMonthlyTopResponseSchema,
    MonthlyTopAwardResponseSchema,
)
from presentation.http.dto.request import VKCallbackSchema
from presentation.http.routers.v1.routers.vk_callbacks.handlers.achievement import (
    send_monthly_top_reward_if_needed,
)
from presentation.http.routers.v1.routers.vk_callbacks.outbound.sender import bind_vk_message_template_service
from presentation.http.routers.v1.routers.vk_callbacks.protocol.payload import VKCallbackPayload

monthly_top_admin_router = APIRouter(route_class=DishkaRoute)


@monthly_top_admin_router.post(
    path="/monthly-top/award",
    name="Начислить monthly_top_10",
    response_model=AwardMonthlyTopResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def award_monthly_top(
    data: AwardMonthlyTopRequestSchema,
    handler: FromDishka[AwardMonthlyTopHandler],
    message_client: FromDishka[IVKMessageClient],
    message_template_service: FromDishka[IVKMessageTemplateService],
) -> AwardMonthlyTopResponseSchema:
    logger.info("Monthly top award requested: month={}, limit={}", data.month, data.limit)

    try:
        result = await handler(AwardMonthlyTopCommand(month=data.month, limit=data.limit))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if not result.achievement_found:
        logger.warning("Monthly top achievement not found: month={}, limit={}", result.month, data.limit)

    fake_payload = VKCallbackPayload(data=VKCallbackSchema(event_id="admin-monthly-top"))
    awards: list[MonthlyTopAwardResponseSchema] = []
    with bind_vk_message_template_service(message_template_service):
        for award in result.awards:
            message_sent = False
            if award.status == MonthlyTopAwardStatus.AWARDED and award.balance_points is not None:
                message_sent = await send_monthly_top_reward_if_needed(
                    data=fake_payload,
                    vk_user_id=award.vk_user_id,
                    users_id=award.users_id,
                    rank=award.rank,
                    points_awarded=award.points_awarded,
                    balance_points=award.balance_points,
                    level_up=award.level_up,
                    message_client=message_client,
                )
                if not message_sent:
                    logger.error(
                        "Monthly top reward message was not sent: month={}, users_id={}, vk_user_id={}",
                        result.month,
                        award.users_id,
                        award.vk_user_id,
                    )

            awards.append(MonthlyTopAwardResponseSchema.from_award(award=award, message_sent=message_sent))

    logger.info(
        "Monthly top award finished: month={}, achievement_found={}, awards={}",
        result.month,
        result.achievement_found,
        len(awards),
    )
    return AwardMonthlyTopResponseSchema(
        month=result.month,
        period_start_at=result.period_start_at,
        period_end_at=result.period_end_at,
        achievement_found=result.achievement_found,
        awards=awards,
    )
