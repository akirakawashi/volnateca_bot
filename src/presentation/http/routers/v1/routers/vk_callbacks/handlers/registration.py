from fastapi.responses import PlainTextResponse
from loguru import logger

from application.command.register_vk_user import RegisterVKUserCommand, RegisterVKUserHandler
from presentation.http.dto.request import VKCallbackSchema
from presentation.http.routers.v1.routers.vk_callbacks.responses import vk_ok_response


async def handle_registration_callback(
    data: VKCallbackSchema,
    interactor: RegisterVKUserHandler,
) -> PlainTextResponse:
    vk_user_id = data.get_vk_user_id()
    if vk_user_id is None:
        logger.warning(
            "TEMP VK registration callback without user id: event_id={}, event_type={}",
            data.event_id,
            data.type,
        )
        return vk_ok_response()

    result = await interactor(
        command_data=RegisterVKUserCommand(
            vk_user_id=vk_user_id,
            first_name=data.get_first_name(),
            last_name=data.get_last_name(),
        ),
    )
    logger.info(
        "TEMP VK registration callback processed: "
        "event_id={}, event_type={}, vk_user_id={}, users_id={}, created={}, screen_name={}",
        data.event_id,
        data.type,
        result.vk_user_id,
        result.users_id,
        result.created,
        result.vk_screen_name,
    )
    return vk_ok_response()
