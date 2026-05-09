from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from presentation.http.dto.request import VKCallbackSchema
from presentation.http.routers.v1.routers.vk_callbacks.dispatcher import VKCallbackDispatcher

vk_callback_router = APIRouter(
    prefix="/vk",
    tags=["VK"],
    route_class=DishkaRoute,
)


@vk_callback_router.post(
    path="/callback",
    name="Обработка события VK Callback API",
    response_class=PlainTextResponse,
    response_model=None,
    responses={200: {"content": {"text/plain": {"example": "ok"}}}},
)
async def vk_callback(
    data: VKCallbackSchema,
    dispatcher: FromDishka[VKCallbackDispatcher],
) -> PlainTextResponse:
    return await dispatcher.handle(data=data)
