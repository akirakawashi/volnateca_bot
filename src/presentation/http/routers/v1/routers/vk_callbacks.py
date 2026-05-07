from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import PlainTextResponse
from loguru import logger

from application.command.register_vk_user import (
    RegisterVKUserCommand,
    RegisterVKUserHandler,
)
from application.common.dto.user import VKUserRegistrationDTO
from presentation.http.dto.request import VKCallbackSchema
from presentation.http.dto.response import OkResponse
from settings.vk import VKSettings

vk_callback_router = APIRouter(
    prefix="/vk",
    tags=["VK"],
    route_class=DishkaRoute,
)


@vk_callback_router.post(
    path="/callback",
    name="Обработка события VK Callback API",
    response_model=None,
    responses={200: {"model": OkResponse[VKUserRegistrationDTO]}},
)
async def vk_callback(
    data: VKCallbackSchema,
    interactor: FromDishka[RegisterVKUserHandler],
    vk_settings: FromDishka[VKSettings],
) -> OkResponse[VKUserRegistrationDTO] | PlainTextResponse:
    if data.is_confirmation():
        return PlainTextResponse(vk_settings.CONFIRMATION_CODE)

    if data.is_like():
        logger.info(
            "TEMP VK like callback received: event_type={}, liker_id={}",
            data.type,
            data.get_like_user_id(),
        )
        return OkResponse[VKUserRegistrationDTO]()

    vk_user_id = data.get_vk_user_id()
    if vk_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="VK user id was not found in callback payload",
        )

    result = await interactor(
        command_data=RegisterVKUserCommand(
            vk_user_id=vk_user_id,
            first_name=data.get_first_name(),
            last_name=data.get_last_name(),
        ),
    )
    return OkResponse(data=result)
