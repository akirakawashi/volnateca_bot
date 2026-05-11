import asyncio
import json
import secrets
from http import HTTPStatus
from typing import Any, Self

import aiohttp
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from application.common.dto.vk import VKUserProfileDTO
from application.interface.clients import IVKMessageClient, IVKUserClient
from settings.vk import VKSettings

VK_USERS_GET_METHOD = "users.get"
VK_USERS_GET_FIELDS = "screen_name"
VK_GROUPS_IS_MEMBER_METHOD = "groups.isMember"
VK_MESSAGES_SEND_METHOD = "messages.send"


class VKAPIErrorSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    error_code: int
    error_msg: str


class VKUserSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    vk_user_id: int = Field(alias="id")
    first_name: str | None = None
    last_name: str | None = None
    screen_name: str | None = None


class VKUsersGetResponseSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    response: list[VKUserSchema] | None = None
    error: VKAPIErrorSchema | None = None


class VKGroupsIsMemberResponseSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    response: int | None = None
    error: VKAPIErrorSchema | None = None


class VKMessagesSendResponseSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    response: int | None = None
    error: VKAPIErrorSchema | None = None


class VKAPIClient(IVKUserClient, IVKMessageClient):
    def __init__(
        self,
        settings: VKSettings,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self._settings = settings
        self._session = session
        self._own_session = session is None

    async def __aenter__(self) -> Self:
        if self._own_session and self._session is None:
            timeout = aiohttp.ClientTimeout(total=self._settings.REQUEST_TIMEOUT_SECONDS)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        if self._own_session and self._session is not None:
            await self._session.close()
            self._session = None

    async def get_user_profile(self, vk_user_id: int) -> VKUserProfileDTO | None:
        if not self._settings.GROUP_ACCESS_TOKEN:
            return None

        response_data = await self._request(
            method=VK_USERS_GET_METHOD,
            params={
                "user_ids": str(vk_user_id),
                "fields": VK_USERS_GET_FIELDS,
                "access_token": self._settings.GROUP_ACCESS_TOKEN,
                "v": self._settings.API_VERSION,
            },
        )
        if response_data is None:
            return None

        try:
            parsed_response = VKUsersGetResponseSchema.model_validate(response_data)
        except ValidationError:
            return None

        if parsed_response.error is not None:
            return None

        if not parsed_response.response:
            return None

        user = parsed_response.response[0]
        return VKUserProfileDTO(
            vk_user_id=user.vk_user_id,
            first_name=user.first_name,
            last_name=user.last_name,
            screen_name=user.screen_name,
        )

    async def is_group_member(self, vk_user_id: int, group_id: int) -> bool | None:
        if not self._settings.GROUP_ACCESS_TOKEN:
            return None

        response_data = await self._request(
            method=VK_GROUPS_IS_MEMBER_METHOD,
            params={
                "group_id": str(abs(group_id)),
                "user_id": str(vk_user_id),
                "access_token": self._settings.GROUP_ACCESS_TOKEN,
                "v": self._settings.API_VERSION,
            },
        )
        if response_data is None:
            return None

        try:
            parsed_response = VKGroupsIsMemberResponseSchema.model_validate(response_data)
        except ValidationError:
            return None

        if parsed_response.error is not None:
            return None

        return bool(parsed_response.response) if parsed_response.response is not None else None

    async def send_message(
        self,
        *,
        vk_user_id: int,
        message: str,
        random_id: int | None = None,
        keyboard: dict[str, object] | None = None,
    ) -> bool:
        if not self._settings.GROUP_ACCESS_TOKEN:
            return False
        if not message:
            return False

        params = {
            "user_id": str(vk_user_id),
            "message": message,
            "random_id": str(random_id if random_id is not None else secrets.randbits(31)),
            "access_token": self._settings.GROUP_ACCESS_TOKEN,
            "v": self._settings.API_VERSION,
        }
        if keyboard is not None:
            params["keyboard"] = json.dumps(keyboard, ensure_ascii=False)

        response_data = await self._request(method=VK_MESSAGES_SEND_METHOD, params=params)
        if response_data is None:
            return False

        try:
            parsed_response = VKMessagesSendResponseSchema.model_validate(response_data)
        except ValidationError:
            return False

        if parsed_response.error is not None:
            return False

        return parsed_response.response is not None

    async def _request(
        self,
        method: str,
        params: dict[str, str],
    ) -> dict[str, Any] | None:
        if self._session is None:
            raise RuntimeError("Сессия клиента VK API не инициализирована")

        url = f"{self._settings.API_BASE_URL.rstrip('/')}/{method}"
        try:
            async with self._session.get(url=url, params=params) as response:
                if response.status != HTTPStatus.OK:
                    return None
                data: Any = await response.json(content_type=None)
                if not isinstance(data, dict):
                    return None
                return data
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return None
