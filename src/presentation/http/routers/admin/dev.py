from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from application.admin.command.seed_dev_scenario import SeedDevScenarioCommand, SeedDevScenarioHandler
from application.command.award_monthly_top import AwardMonthlyTopCommand, AwardMonthlyTopHandler
from application.interface.clients import IVKMessageClient
from presentation.http.dto.admin.dev import (
    AwardMonthlyTopRequest,
    AwardMonthlyTopResponse,
    SeedDevScenarioRequest,
    SeedDevScenarioResponse,
)
from presentation.http.dto.request import VKCallbackSchema
from presentation.http.routers.v1.routers.vk_callbacks.handlers.achievement import send_monthly_top_reward_if_needed
from presentation.http.routers.v1.routers.vk_callbacks.payload import VKCallbackPayload

# TODO: удалить dev_admin_router перед релизом — только для локальной отладки.
dev_admin_router = APIRouter(route_class=DishkaRoute)


@dev_admin_router.post(
    path="/dev/seed",
    name="Засеять dev-сценарий",
    response_model=SeedDevScenarioResponse,
    status_code=200,
)
async def seed_dev_scenario(
    data: SeedDevScenarioRequest,
    handler: FromDishka[SeedDevScenarioHandler],
) -> SeedDevScenarioResponse:
    result = await handler(
        SeedDevScenarioCommand(scenario=data.scenario, users_id=data.users_id),
    )
    return SeedDevScenarioResponse(messages=list(result.messages))


@dev_admin_router.post(
    path="/dev/award-monthly-top",
    name="Начислить monthly_top_10",
    response_model=AwardMonthlyTopResponse,
    status_code=200,
)
async def award_monthly_top_dev(
    data: AwardMonthlyTopRequest,
    handler: FromDishka[AwardMonthlyTopHandler],
    message_client: FromDishka[IVKMessageClient],
) -> AwardMonthlyTopResponse:
    result = await handler(AwardMonthlyTopCommand(month=data.month, limit=data.limit))
    fake_payload = VKCallbackPayload(data=VKCallbackSchema(event_id="dev-manual"))

    messages = [f"Month: {result.month}"]
    for award in result.awards:
        messages.append(
            f"#{award.rank}: users_id={award.users_id}, vk_user_id={award.vk_user_id}, "
            f"status={award.status.value}, awarded={award.points_awarded}, balance={award.balance_points}",
        )

        if award.status.value == "awarded" and award.balance_points is not None:
            await send_monthly_top_reward_if_needed(
                data=fake_payload,
                vk_user_id=award.vk_user_id,
                users_id=award.users_id,
                rank=award.rank,
                points_awarded=award.points_awarded,
                balance_points=award.balance_points,
                level_up=award.level_up,
                message_client=message_client,
            )

    return AwardMonthlyTopResponse(month=result.month, messages=messages)
