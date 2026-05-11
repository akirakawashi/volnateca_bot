from dataclasses import dataclass
import json
from typing import Any, Type, TypeVar

from pydantic import BaseModel, ValidationError

from application.common.dto.vk import VKWallPostDTO
from presentation.http.dto.request import VKCallbackSchema, VKCallbackWallPostSchema
from presentation.http.routers.v1.routers.vk_callbacks.event_objects import (
    VKCallbackEventObjectSchema,
    VKLikeObjectSchema,
    VKMessageObjectSchema,
    VKRepostObjectSchema,
    VKUserObjectSchema,
    VKWallPostObjectSchema,
)
from presentation.http.routers.v1.routers.vk_callbacks.event_types import VKEventGroups, VKEventType

EventObjectT = TypeVar("EventObjectT", bound=VKCallbackEventObjectSchema)


@dataclass(slots=True, frozen=True)
class VKCallbackPayload:
    data: VKCallbackSchema

    # Метаданные события VK

    @property
    def type(self) -> str | None:
        return self.data.type

    @property
    def group_id(self) -> int | None:
        return self.data.group_id

    @property
    def event_id(self) -> str | None:
        return self.data.event_id

    # Классификация событий

    def is_confirmation(self) -> bool:
        return self.type == VKEventType.CONFIRMATION

    def is_like(self) -> bool:
        return self.type in VKEventGroups.LIKE

    def is_repost(self) -> bool:
        return self.type in VKEventGroups.REPOST

    def is_subscription_event(self) -> bool:
        return self.type in VKEventGroups.SUBSCRIPTION

    def is_wall_post_new(self) -> bool:
        return self.type in VKEventGroups.WALL_POST

    def is_registration_event(self) -> bool:
        return self.type in VKEventGroups.REGISTRATION

    def is_message_new(self) -> bool:
        return self.type == VKEventType.MESSAGE_NEW

    # Проверка события VK

    def is_expected_group(self, expected_group_id: int) -> bool:
        return self.group_id == expected_group_id

    def has_valid_secret(self, expected_secret: str) -> bool:
        return self.data.secret == expected_secret

    # Извлечение пользователя

    def get_like_user_id(self) -> int | None:
        like_object = self.get_like_object()
        return self._normalize_vk_user_id(raw_user_id=like_object.liker_id if like_object else None)

    def get_primary_vk_user_id(self) -> int | None:
        if self.is_like():
            return self.get_like_user_id()
        if self.is_repost():
            return self.get_repost_user_id()
        return self.get_vk_user_id()

    def get_repost_user_id(self) -> int | None:
        repost_object = self.get_repost_object()
        if repost_object is None:
            return None

        from_id = self._normalize_vk_user_id(raw_user_id=repost_object.from_id)
        wall_owner_id = self._normalize_vk_user_id(raw_user_id=repost_object.owner_id)

        # Засчитываем только репосты, опубликованные на стене самого пользователя.
        if from_id is None or wall_owner_id is None or from_id != wall_owner_id:
            return None

        return from_id

    def get_vk_user_id(self) -> int | None:
        message_object = self.get_message_object()
        message = message_object.message if message_object is not None else None
        user_object = self.get_user_object()
        raw_user_id: Any = (
            message.from_id
            if message and message.from_id is not None
            else message.user_id
            if message and message.user_id is not None
            else user_object.user_id
            if user_object and user_object.user_id is not None
            else user_object.from_id
            if user_object is not None
            else None
        )

        return self._normalize_vk_user_id(raw_user_id=raw_user_id)

    def get_first_name(self) -> str | None:
        user_object = self.get_user_object()
        if user_object is not None and user_object.first_name:
            return user_object.first_name

        message_object = self.get_message_object()
        if message_object is not None and message_object.message.first_name:
            return message_object.message.first_name
        return None

    def get_last_name(self) -> str | None:
        user_object = self.get_user_object()
        if user_object is not None and user_object.last_name:
            return user_object.last_name

        message_object = self.get_message_object()
        if message_object is not None and message_object.message.last_name:
            return message_object.message.last_name
        return None

    def get_message_text(self) -> str:
        message_object = self.get_message_object()
        message = message_object.message if message_object is not None else None
        return message.text if message and message.text is not None else ""

    def get_button_payload(self) -> dict[str, Any] | None:
        """Возвращает распарсенный JSON payload нажатой кнопки клавиатуры VK.

        VK передаёт payload как строку с JSON внутри message.payload.
        Возвращает None если payload отсутствует или не является валидным JSON-объектом.
        """
        message_object = self.get_message_object()
        message = message_object.message if message_object is not None else None
        raw = message.payload if message and message.payload is not None else None
        if raw is None:
            return None
        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            return None
        return parsed if isinstance(parsed, dict) else None

    # Извлечение постов

    def get_liked_post(self) -> VKWallPostDTO | None:
        like_object = self.get_like_object()
        if like_object is None:
            return None
        return VKWallPostDTO(
            owner_id=like_object.object_owner_id,
            post_id=like_object.object_id,
        )

    def get_liked_post_external_ids(self) -> tuple[str, ...]:
        post = self.get_liked_post()
        if post is None:
            return ()
        return post.external_id_variants

    def get_repost_external_id(self) -> str | None:
        post = self.get_wall_post()
        return post.external_id if post is not None else None

    def get_reposted_wall_post_external_ids(self) -> tuple[str, ...]:
        repost_object = self.get_repost_object()
        if repost_object is None:
            return ()

        external_ids: set[str] = set()
        for copied_post in repost_object.copy_history:
            post = self._to_wall_post_dto(copied_post=copied_post)
            if post is not None:
                external_ids.update(post.external_id_variants)
        return tuple(sorted(external_ids))

    def get_wall_post(self) -> VKWallPostDTO | None:
        wall_post_object = self.get_wall_post_object()
        if wall_post_object is None:
            return None

        return VKWallPostDTO(
            owner_id=wall_post_object.owner_id,
            post_id=wall_post_object.post_id,
        )

    def get_wall_post_text(self) -> str:
        wall_post_object = self.get_wall_post_object()
        return wall_post_object.text if wall_post_object and wall_post_object.text else ""

    # Извлечение типизированного объекта события

    def get_like_object(self) -> VKLikeObjectSchema | None:
        if not self.is_like():
            return None
        return self._parse_event_object(schema=VKLikeObjectSchema)

    def get_repost_object(self) -> VKRepostObjectSchema | None:
        if not self.is_repost():
            return None
        return self._parse_event_object(schema=VKRepostObjectSchema)

    def get_wall_post_object(self) -> VKWallPostObjectSchema | None:
        return self._parse_event_object(schema=VKWallPostObjectSchema)

    def get_message_object(self) -> VKMessageObjectSchema | None:
        return self._parse_event_object(schema=VKMessageObjectSchema)

    def get_user_object(self) -> VKUserObjectSchema | None:
        return self._parse_event_object(schema=VKUserObjectSchema)

    # Помощники для логирования

    def get_event_object_keys(self) -> tuple[str, ...]:
        return self._get_present_keys(model=self.data.event_object)

    def get_message_keys(self) -> tuple[str, ...]:
        if self.data.event_object.message is None:
            return ()
        return self._get_present_keys(model=self.data.event_object.message)

    # Внутренняя логика

    @staticmethod
    def _to_wall_post_dto(copied_post: VKCallbackWallPostSchema) -> VKWallPostDTO | None:
        if copied_post.owner_id is None or copied_post.post_id is None:
            return None
        return VKWallPostDTO(owner_id=copied_post.owner_id, post_id=copied_post.post_id)

    def _parse_event_object(self, *, schema: Type[EventObjectT]) -> EventObjectT | None:
        try:
            return schema.model_validate(self.data.event_object.model_dump(by_alias=True))
        except ValidationError:
            return None

    @staticmethod
    def _get_present_keys(model: BaseModel) -> tuple[str, ...]:
        extra_keys = set(model.model_extra or {})
        return tuple(sorted(model.model_fields_set | extra_keys))

    @staticmethod
    def _normalize_vk_user_id(raw_user_id: Any) -> int | None:
        if raw_user_id is None:
            return None

        vk_user_id = int(raw_user_id)
        return vk_user_id if vk_user_id > 0 else None
