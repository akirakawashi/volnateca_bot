from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from application.command.complete_vk_repost_task import CompleteVKRepostTaskHandler
from application.command.create_vk_repost_task_from_wall_post import (
    CreateVKRepostTaskFromWallPostHandler,
)
from application.command.register_vk_user import RegisterVKUserHandler
from presentation.http.dto.request import VKCallbackSchema
from presentation.http.routers.v1.routers.vk_callbacks.dispatcher import VKCallbackDispatcher
from settings.vk import VKSettings

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
    register_vk_user_interactor: FromDishka[RegisterVKUserHandler],
    complete_vk_repost_task_interactor: FromDishka[CompleteVKRepostTaskHandler],
    create_vk_repost_task_interactor: FromDishka[CreateVKRepostTaskFromWallPostHandler],
    vk_settings: FromDishka[VKSettings],
) -> PlainTextResponse:
    dispatcher = VKCallbackDispatcher(
        vk_settings=vk_settings,
        register_vk_user_interactor=register_vk_user_interactor,
        complete_vk_repost_task_interactor=complete_vk_repost_task_interactor,
        create_vk_repost_task_interactor=create_vk_repost_task_interactor,
    )
    return await dispatcher.handle(data=data)
