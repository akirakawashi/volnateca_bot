from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from application.common.dto.vk import VKWallPostDTO
from presentation.http.dto.request import VKCallbackSchema, VKCallbackWallPostSchema
from presentation.http.routers.v1.routers.vk_callbacks.event_types import VKEventGroups, VKEventType


@dataclass(slots=True, frozen=True)
class VKCallbackPayload:
    data: VKCallbackSchema

    # Callback metadata

    @property
    def type(self) -> str | None:
        return self.data.type

    @property
    def group_id(self) -> int | None:
        return self.data.group_id

    @property
    def event_id(self) -> str | None:
        return self.data.event_id

    # Event classification

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

    # Callback validation

    def is_expected_group(self, expected_group_id: int) -> bool:
        return self.group_id == expected_group_id

    def has_valid_secret(self, expected_secret: str) -> bool:
        return self.data.secret == expected_secret

    # User extraction

    def get_like_user_id(self) -> int | None:
        return self._normalize_vk_user_id(raw_user_id=self.data.event_object.liker_id)

    def get_primary_vk_user_id(self) -> int | None:
        if self.is_like():
            return self.get_like_user_id()
        if self.is_repost():
            return self.get_repost_user_id()
        return self.get_vk_user_id()

    def get_repost_user_id(self) -> int | None:
        from_id = self._normalize_vk_user_id(raw_user_id=self.data.event_object.from_id)
        wall_owner_id = self._normalize_vk_user_id(raw_user_id=self.data.event_object.owner_id)

        # Count only reposts published on the reposting user's own wall.
        if from_id is None or wall_owner_id is None or from_id != wall_owner_id:
            return None

        return from_id

    def get_vk_user_id(self) -> int | None:
        message = self.data.event_object.message
        raw_user_id: Any = (
            message.from_id
            if message and message.from_id is not None
            else message.user_id
            if message and message.user_id is not None
            else self.data.event_object.user_id
            if self.data.event_object.user_id is not None
            else self.data.event_object.from_id
        )

        return self._normalize_vk_user_id(raw_user_id=raw_user_id)

    def get_first_name(self) -> str | None:
        if self.data.event_object.first_name:
            return self.data.event_object.first_name
        if self.data.event_object.message and self.data.event_object.message.first_name:
            return self.data.event_object.message.first_name
        return None

    def get_last_name(self) -> str | None:
        if self.data.event_object.last_name:
            return self.data.event_object.last_name
        if self.data.event_object.message and self.data.event_object.message.last_name:
            return self.data.event_object.message.last_name
        return None

    def get_message_text(self) -> str:
        message = self.data.event_object.message
        return message.text if message and message.text is not None else ""

    # Post extraction

    def get_liked_post(self) -> VKWallPostDTO | None:
        obj = self.data.event_object
        if obj.object_type != "post" or obj.object_id is None or obj.object_owner_id is None:
            return None
        return VKWallPostDTO(owner_id=obj.object_owner_id, post_id=obj.object_id)

    def get_liked_post_external_ids(self) -> tuple[str, ...]:
        post = self.get_liked_post()
        if post is None:
            return ()
        return post.external_id_variants

    def get_repost_external_id(self) -> str | None:
        post = self.get_wall_post()
        return post.external_id if post is not None else None

    def get_reposted_wall_post_external_ids(self) -> tuple[str, ...]:
        external_ids: set[str] = set()
        for copied_post in self.data.event_object.copy_history:
            post = self._to_wall_post_dto(copied_post=copied_post)
            if post is not None:
                external_ids.update(post.external_id_variants)
        return tuple(sorted(external_ids))

    def get_wall_post(self) -> VKWallPostDTO | None:
        if self.data.event_object.owner_id is None or self.data.event_object.post_id is None:
            return None

        return VKWallPostDTO(
            owner_id=self.data.event_object.owner_id,
            post_id=self.data.event_object.post_id,
        )

    def get_wall_post_text(self) -> str:
        return self.data.event_object.text or ""

    # Logging helpers

    def get_event_object_keys(self) -> tuple[str, ...]:
        return self._get_present_keys(model=self.data.event_object)

    def get_message_keys(self) -> tuple[str, ...]:
        if self.data.event_object.message is None:
            return ()
        return self._get_present_keys(model=self.data.event_object.message)

    # Internals

    @staticmethod
    def _to_wall_post_dto(copied_post: VKCallbackWallPostSchema) -> VKWallPostDTO | None:
        if copied_post.owner_id is None or copied_post.post_id is None:
            return None
        return VKWallPostDTO(owner_id=copied_post.owner_id, post_id=copied_post.post_id)

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
