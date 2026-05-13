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
VK_PHOTOS_GET_MESSAGES_UPLOAD_SERVER_METHOD = "photos.getMessagesUploadServer"
VK_PHOTOS_SAVE_MESSAGES_PHOTO_METHOD = "photos.saveMessagesPhoto"


class VKAPIErrorSchema(BaseModel):
    """Объект ошибки, который VK API возвращает вместо response при сбое."""

    model_config = ConfigDict(extra="allow")

    error_code: int
    error_msg: str


class VKUserSchema(BaseModel):
    """Данные одного пользователя из ответа users.get."""

    model_config = ConfigDict(extra="allow")

    vk_user_id: int = Field(alias="id")
    first_name: str | None = None
    last_name: str | None = None
    screen_name: str | None = None


class VKUsersGetResponseSchema(BaseModel):
    """Полный ответ метода users.get."""

    model_config = ConfigDict(extra="allow")

    response: list[VKUserSchema] | None = None
    error: VKAPIErrorSchema | None = None


class VKGroupsIsMemberResponseSchema(BaseModel):
    """Полный ответ метода groups.isMember.

    response: 1 — пользователь состоит в группе, 0 — не состоит.
    """

    model_config = ConfigDict(extra="allow")

    response: int | None = None
    error: VKAPIErrorSchema | None = None


class VKMessagesSendResponseSchema(BaseModel):
    """Полный ответ метода messages.send.

    response содержит идентификатор отправленного сообщения при успехе.
    """

    model_config = ConfigDict(extra="allow")

    response: int | None = None
    error: VKAPIErrorSchema | None = None


class VKMessagesUploadServerSchema(BaseModel):
    """Объект внутри ответа photos.getMessagesUploadServer.

    Содержит URL сервера, на который нужно POST-ом загрузить файл фото.
    """

    model_config = ConfigDict(extra="allow")

    upload_url: str


class VKGetMessagesUploadServerResponseSchema(BaseModel):
    """Полный ответ метода photos.getMessagesUploadServer (шаг 1 загрузки фото)."""

    model_config = ConfigDict(extra="allow")

    response: VKMessagesUploadServerSchema | None = None
    error: VKAPIErrorSchema | None = None


class VKPhotoUploadResultSchema(BaseModel):
    """Ответ самого upload-сервера VK после POST с файлом (шаг 2).

    Не является ответом VK API — возвращается upload_url-сервером напрямую.
    Поля server, photo и hash нужно передать в photos.saveMessagesPhoto.
    """

    model_config = ConfigDict(extra="allow")

    server: int
    photo: str
    hash: str


class VKSavedMessagePhotoSchema(BaseModel):
    """Один элемент массива response из photos.saveMessagesPhoto (шаг 3).

    owner_id и id используются для формирования строки вложения photo{owner_id}_{id}.
    """

    model_config = ConfigDict(extra="allow")

    id: int
    owner_id: int


class VKSaveMessagesPhotoResponseSchema(BaseModel):
    """Полный ответ метода photos.saveMessagesPhoto (шаг 3 загрузки фото)."""

    model_config = ConfigDict(extra="allow")

    response: list[VKSavedMessagePhotoSchema] | None = None
    error: VKAPIErrorSchema | None = None


class VKAPIClient(IVKUserClient, IVKMessageClient):
    """Небросающий клиент VK API для application-слоя.

    Методы возвращают None/False при недоступном токене, сетевой ошибке,
    ошибке VK API или неожиданном формате ответа. Это позволяет use-case-ам
    принимать решение без обработки инфраструктурных исключений.
    """

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
        """Закрывает aiohttp-сессию, если клиент создал её сам."""

        if self._own_session and self._session is not None:
            await self._session.close()
            self._session = None

    async def get_user_profile(self, vk_user_id: int) -> VKUserProfileDTO | None:
        """Запрашивает профиль пользователя через users.get."""

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
        """Проверяет членство пользователя в группе через groups.isMember."""

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
        attachment: str | None = None,
    ) -> bool:
        """Отправляет сообщение VK и возвращает факт успешного ответа API."""

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
        if attachment is not None:
            params["attachment"] = attachment

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

    async def upload_photo_for_message(self, image_url: str) -> str | None:
        """Загружает изображение по URL на серверы VK и возвращает строку вложения.

        Реализует трёхшаговый процесс:
        1. Получает адрес сервера загрузки через photos.getMessagesUploadServer.
        2. Скачивает файл изображения и загружает его на VK.
        3. Сохраняет фото через photos.saveMessagesPhoto.
        """

        if not self._settings.GROUP_ACCESS_TOKEN:
            return None
        if self._session is None:
            return None

        # 1. Получаем URL сервера загрузки
        upload_server_data = await self._request(
            method=VK_PHOTOS_GET_MESSAGES_UPLOAD_SERVER_METHOD,
            params={
                "access_token": self._settings.GROUP_ACCESS_TOKEN,
                "v": self._settings.API_VERSION,
            },
        )
        if upload_server_data is None:
            return None

        try:
            upload_server = VKGetMessagesUploadServerResponseSchema.model_validate(upload_server_data)
        except ValidationError:
            return None

        if upload_server.error is not None or upload_server.response is None:
            return None

        upload_url = upload_server.response.upload_url

        # 2. Скачиваем изображение и загружаем на VK
        try:
            async with self._session.get(image_url) as image_response:
                if image_response.status != HTTPStatus.OK:
                    return None
                image_data = await image_response.read()
                content_type = image_response.content_type or "image/jpeg"
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return None

        try:
            form = aiohttp.FormData()
            form.add_field("photo", image_data, filename="photo.jpg", content_type=content_type)
            async with self._session.post(upload_url, data=form) as upload_response:
                if upload_response.status != HTTPStatus.OK:
                    return None
                upload_result: Any = await upload_response.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return None

        if not isinstance(upload_result, dict):
            return None

        try:
            uploaded = VKPhotoUploadResultSchema.model_validate(upload_result)
        except ValidationError:
            return None

        # 3. Сохраняем фото через photos.saveMessagesPhoto
        save_data = await self._request(
            method=VK_PHOTOS_SAVE_MESSAGES_PHOTO_METHOD,
            params={
                "photo": uploaded.photo,
                "server": str(uploaded.server),
                "hash": uploaded.hash,
                "access_token": self._settings.GROUP_ACCESS_TOKEN,
                "v": self._settings.API_VERSION,
            },
        )
        if save_data is None:
            return None

        try:
            saved = VKSaveMessagesPhotoResponseSchema.model_validate(save_data)
        except ValidationError:
            return None

        if saved.error is not None or not saved.response:
            return None

        photo: VKSavedMessagePhotoSchema = saved.response[0]
        return f"photo{photo.owner_id}_{photo.id}"

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
