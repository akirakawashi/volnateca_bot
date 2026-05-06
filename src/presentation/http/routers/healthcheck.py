from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from presentation.http.dto.response import HEALTHCHECK_RESPONSE

healthcheck_router = APIRouter(tags=["Service"], route_class=DishkaRoute)


@healthcheck_router.get("/healthcheck", responses=HEALTHCHECK_RESPONSE)
async def healthcheck() -> JSONResponse:
    return JSONResponse(status_code=200, content={"status": "ok"})
