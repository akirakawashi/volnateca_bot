import asyncio
from http import HTTPStatus
from typing import Any, Self

import aiohttp
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from application.common.dto.vk import VKUserProfileDTO, VKWallPostDTO
from application.interface.clients import IVKUserClient
from settings.vk import VKSettings

VK_USERS_GET_METHOD = "users.get"
VK_USERS_GET_FIELDS = "screen_name"
VK_GROUPS_IS_MEMBER_METHOD = "groups.isMember"
VK_LIKES_IS_LIKED_METHOD = "likes.isLiked"
VK_LIKE_OBJECT_TYPE_POST = "post"


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

    response: bool | None = None
    error: VKAPIErrorSchema | None = None


class VKLikesIsLikedSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    liked: bool = False
    copied: bool = False


class VKLikesIsLikedResponseSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    response: VKLikesIsLikedSchema | None = None
    error: VKAPIErrorSchema | None = None


class VKAPIClient(IVKUserClient):
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
            logger.warning("TEMP VK users.get skipped: group access token is not configured")
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
        except ValidationError as err:
            logger.warning(
                "TEMP VK users.get response validation failed: vk_user_id={}, error={}",
                vk_user_id,
                err,
            )
            return None

        if parsed_response.error is not None:
            logger.warning(
                "TEMP VK users.get returned error: vk_user_id={}, error_code={}, error_msg={}",
                vk_user_id,
                parsed_response.error.error_code,
                parsed_response.error.error_msg,
            )
            return None

        if not parsed_response.response:
            logger.warning("TEMP VK users.get returned empty profile: vk_user_id={}", vk_user_id)
            return None

        user = parsed_response.response[0]
        profile = VKUserProfileDTO(
            vk_user_id=user.vk_user_id,
            first_name=user.first_name,
            last_name=user.last_name,
            screen_name=user.screen_name,
        )
        logger.info(
            "TEMP VK user profile fetched: vk_user_id={}, screen_name={}, profile_url={}, stable_profile_url={}",
            profile.vk_user_id,
            profile.screen_name,
            profile.profile_url,
            profile.stable_profile_url,
        )
        return profile

    async def is_group_member(self, vk_user_id: int, group_id: int) -> bool | None:
        if not self._settings.GROUP_ACCESS_TOKEN:
            logger.warning("TEMP VK groups.isMember skipped: group access token is not configured")
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
        except ValidationError as err:
            logger.warning(
                "TEMP VK groups.isMember response validation failed: "
                "vk_user_id={}, group_id={}, error={}",
                vk_user_id,
                group_id,
                err,
            )
            return None

        if parsed_response.error is not None:
            logger.warning(
                "TEMP VK groups.isMember returned error: "
                "vk_user_id={}, group_id={}, error_code={}, error_msg={}",
                vk_user_id,
                group_id,
                parsed_response.error.error_code,
                parsed_response.error.error_msg,
            )
            return None

        return parsed_response.response

    async def has_user_reposted_wall_post(
        self,
        vk_user_id: int,
        post: VKWallPostDTO,
    ) -> bool | None:
        if not self._settings.GROUP_ACCESS_TOKEN:
            logger.warning("TEMP VK likes.isLiked skipped: group access token is not configured")
            return None

        response_data = await self._request(
            method=VK_LIKES_IS_LIKED_METHOD,
            params={
                "type": VK_LIKE_OBJECT_TYPE_POST,
                "owner_id": str(post.owner_id),
                "item_id": str(post.post_id),
                "user_id": str(vk_user_id),
                "access_token": self._settings.GROUP_ACCESS_TOKEN,
                "v": self._settings.API_VERSION,
            },
        )
        if response_data is None:
            return None

        try:
            parsed_response = VKLikesIsLikedResponseSchema.model_validate(response_data)
        except ValidationError as err:
            logger.warning(
                "TEMP VK likes.isLiked response validation failed: "
                "vk_user_id={}, post_external_id={}, error={}",
                vk_user_id,
                post.external_id,
                err,
            )
            return None

        if parsed_response.error is not None:
            logger.warning(
                "TEMP VK likes.isLiked returned error: "
                "vk_user_id={}, post_external_id={}, error_code={}, error_msg={}",
                vk_user_id,
                post.external_id,
                parsed_response.error.error_code,
                parsed_response.error.error_msg,
            )
            return None

        return parsed_response.response.copied if parsed_response.response is not None else None

    async def _request(
        self,
        method: str,
        params: dict[str, str],
    ) -> dict[str, Any] | None:
        if self._session is None:
            raise RuntimeError("VK API client session is not initialized")

        url = f"{self._settings.API_BASE_URL.rstrip('/')}/{method}"
        try:
            async with self._session.get(url=url, params=params) as response:
                if response.status != HTTPStatus.OK:
                    logger.warning(
                        "TEMP VK API request failed: method={}, status_code={}",
                        method,
                        response.status,
                    )
                    return None
                data: Any = await response.json(content_type=None)
                if not isinstance(data, dict):
                    logger.warning("TEMP VK API returned non-object response: method={}", method)
                    return None
                return data
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            logger.warning("TEMP VK API request error: method={}, error={}", method, err)
            return None
