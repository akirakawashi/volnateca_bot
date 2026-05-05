from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

healthcheck_router = APIRouter(tags=["Service"], route_class=DishkaRoute)


@healthcheck_router.get("/healthcheck")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
