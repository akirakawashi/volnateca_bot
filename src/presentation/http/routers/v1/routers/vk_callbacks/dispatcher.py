from dataclasses import dataclass

from fastapi import HTTPException, status
from fastapi.responses import PlainTextResponse
from loguru import logger

from application.command.complete_vk_like_task import CompleteVKLikeTaskHandler
from application.command.complete_vk_repost_task import CompleteVKRepostTaskHandler
from application.command.complete_vk_subscription_task import CompleteVKSubscriptionTaskHandler
from application.command.create_vk_post_tasks import CreateVKPostTasksHandler
from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionHandler,
)
from presentation.http.dto.request import VKCallbackSchema
from presentation.http.routers.v1.routers.vk_callbacks.handlers import (
    handle_confirmation_callback,
    handle_ignored_callback,
    handle_like_callback,
    handle_registration_callback,
    handle_repost_callback,
    handle_subscription_callback,
    handle_wall_post_new_callback,
)
from presentation.http.routers.v1.routers.vk_callbacks.payload import VKCallbackPayload
from settings.vk import VKSettings


@dataclass(slots=True, frozen=True, kw_only=True)
class VKCallbackDispatcher:
    vk_settings: VKSettings
    register_vk_user_and_check_subscription_interactor: RegisterVKUserAndCheckSubscriptionHandler
    complete_vk_repost_task_interactor: CompleteVKRepostTaskHandler
    complete_vk_subscription_task_interactor: CompleteVKSubscriptionTaskHandler
    create_vk_post_tasks_interactor: CreateVKPostTasksHandler
    complete_vk_like_task_interactor: CompleteVKLikeTaskHandler

    async def handle(self, data: VKCallbackSchema) -> PlainTextResponse:
        payload = VKCallbackPayload(data=data)
        self._validate_group(payload=payload)

        if payload.is_confirmation():
            return handle_confirmation_callback(vk_settings=self.vk_settings)

        self._validate_secret(payload=payload)
        self._log_callback(payload=payload)

        if payload.is_like():
            return await handle_like_callback(
                data=payload,
                interactor_complete=self.complete_vk_like_task_interactor,
            )

        if payload.is_wall_post_new():
            return await handle_wall_post_new_callback(
                data=payload,
                interactor=self.create_vk_post_tasks_interactor,
            )

        if payload.is_repost():
            return await handle_repost_callback(
                data=payload,
                interactor=self.complete_vk_repost_task_interactor,
            )

        if payload.is_subscription_event():
            return await handle_subscription_callback(
                data=payload,
                interactor=self.complete_vk_subscription_task_interactor,
            )

        if payload.is_registration_event():
            return await handle_registration_callback(
                data=payload,
                interactor=self.register_vk_user_and_check_subscription_interactor,
            )

        return handle_ignored_callback(data=payload)

    def _validate_group(self, payload: VKCallbackPayload) -> None:
        if payload.is_expected_group(expected_group_id=self.vk_settings.GROUP_ID):
            return

        logger.warning(
            "TEMP VK callback rejected by group_id: event_type={}, group_id={}",
            payload.type,
            payload.group_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unexpected VK group id",
        )

    def _validate_secret(self, payload: VKCallbackPayload) -> None:
        if payload.has_valid_secret(expected_secret=self.vk_settings.SECRET_KEY):
            return

        logger.warning(
            "TEMP VK callback rejected by secret: event_id={}, event_type={}, group_id={}",
            payload.event_id,
            payload.type,
            payload.group_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid VK callback secret",
        )

    @staticmethod
    def _log_callback(payload: VKCallbackPayload) -> None:
        logger.info(
            "TEMP VK callback received: "
            "event_id={}, event_type={}, group_id={}, vk_user_id={}, object_keys={}, message_keys={}",
            payload.event_id,
            payload.type,
            payload.group_id,
            payload.get_primary_vk_user_id(),
            payload.get_event_object_keys(),
            payload.get_message_keys(),
        )
