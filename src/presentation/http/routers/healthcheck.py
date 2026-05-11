from typing import Any

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi.responses import JSONResponse

healthcheck_router = APIRouter(tags=["Service"], route_class=DishkaRoute)

HEALTHCHECK_RESPONSE: dict[int | str, dict[str, Any]] = {
    200: {"content": {"application/json": {"example": {"status": "ok"}}}},
    500: {"content": {"application/json": {"example": {"status": "error", "detail": "string"}}}},
}


@healthcheck_router.get("/healthcheck", responses=HEALTHCHECK_RESPONSE)
async def healthcheck() -> JSONResponse:
    return JSONResponse(status_code=200, content={"status": "ok"})
