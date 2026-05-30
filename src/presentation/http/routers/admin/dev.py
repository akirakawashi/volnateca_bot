from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from application.admin.command.seed_dev_scenario import SeedDevScenarioCommand, SeedDevScenarioHandler
from application.admin.command.seed_store_prizes import SeedStorePrizesCommand, SeedStorePrizesHandler
from presentation.http.dto.admin.dev import (
    SeedDevScenarioRequest,
    SeedDevScenarioResponse,
    SeedStorePrizesResponse,
)

# TODO DEV: удалить весь файл dev.py перед релизом — только для локальной отладки.
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
    # TODO DEV: удалить endpoint /dev/seed перед релизом.
    result = await handler(
        SeedDevScenarioCommand(scenario=data.scenario, users_id=data.users_id),
    )
    return SeedDevScenarioResponse(messages=list(result.messages))


@dev_admin_router.post(
    path="/dev/seed-store-prizes",
    name="Засеять тестовые призы магазина",
    response_model=SeedStorePrizesResponse,
    status_code=200,
)
async def seed_store_prizes(
    handler: FromDishka[SeedStorePrizesHandler],
) -> SeedStorePrizesResponse:
    # TODO DEV: удалить endpoint /dev/seed-store-prizes перед релизом.
    result = await handler(SeedStorePrizesCommand())
    return SeedStorePrizesResponse(messages=list(result.messages))
