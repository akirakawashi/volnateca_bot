from dataclasses import dataclass

from fastapi import HTTPException, status
from fastapi.responses import PlainTextResponse
from loguru import logger

from application.command.register_vk_user import RegisterVKUserHandler
from presentation.http.dto.request import VKCallbackSchema
from presentation.http.routers.v1.routers.vk_callbacks.handlers import (
    handle_confirmation_callback,
    handle_ignored_callback,
    handle_like_callback,
    handle_registration_callback,
)
from settings.vk import VKSettings


@dataclass(slots=True, frozen=True, kw_only=True)
class VKCallbackDispatcher:
    vk_settings: VKSettings
    register_vk_user_interactor: RegisterVKUserHandler

    async def handle(self, data: VKCallbackSchema) -> PlainTextResponse:
        self._validate_group(data=data)

        if data.is_confirmation():
            return handle_confirmation_callback(vk_settings=self.vk_settings)

        self._validate_secret(data=data)
        self._log_callback(data=data)

        if data.is_like():
            return handle_like_callback(data=data)

        if data.is_registration_event():
            return await handle_registration_callback(
                data=data,
                interactor=self.register_vk_user_interactor,
            )

        return handle_ignored_callback(data=data)

    def _validate_group(self, data: VKCallbackSchema) -> None:
        if data.is_expected_group(expected_group_id=self.vk_settings.GROUP_ID):
            return

        logger.warning(
            "TEMP VK callback rejected by group_id: event_type={}, group_id={}",
            data.type,
            data.group_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unexpected VK group id",
        )

    def _validate_secret(self, data: VKCallbackSchema) -> None:
        if data.has_valid_secret(expected_secret=self.vk_settings.SECRET_KEY):
            return

        logger.warning(
            "TEMP VK callback rejected by secret: event_id={}, event_type={}, group_id={}",
            data.event_id,
            data.type,
            data.group_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid VK callback secret",
        )

    @staticmethod
    def _log_callback(data: VKCallbackSchema) -> None:
        logger.info(
            "TEMP VK callback received: "
            "event_id={}, event_type={}, group_id={}, vk_user_id={}, object_keys={}, message_keys={}",
            data.event_id,
            data.type,
            data.group_id,
            data.get_primary_vk_user_id(),
            data.get_event_object_keys(),
            data.get_message_keys(),
        )
