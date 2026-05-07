from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from application.common.dto.vk import VKWallPostDTO

VK_CONFIRMATION_EVENT_TYPE = "confirmation"
VK_LIKE_EVENT_TYPES = frozenset(("like_add", "like_remove"))
VK_REGISTRATION_EVENT_TYPES = frozenset(("message_new", "message_allow"))
VK_REPOST_EVENT_TYPES = frozenset(("wall_repost",))
VK_SUBSCRIPTION_EVENT_TYPES = frozenset(("group_join",))
VK_WALL_POST_EVENT_TYPES = frozenset(("wall_post_new",))


class VKCallbackMessageSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    from_id: int | None = Field(default=None, description="ID пользователя VK")
    user_id: int | None = Field(default=None, description="ID пользователя VK")
    first_name: str | None = Field(default=None, description="Имя пользователя VK")
    last_name: str | None = Field(default=None, description="Фамилия пользователя VK")


class VKCallbackWallPostSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    post_id: int | None = Field(default=None, alias="id", description="ID записи на стене VK")
    owner_id: int | None = Field(default=None, description="ID владельца стены VK")

    def to_wall_post_dto(self) -> VKWallPostDTO | None:
        if self.owner_id is None or self.post_id is None:
            return None
        return VKWallPostDTO(owner_id=self.owner_id, post_id=self.post_id)


class VKCallbackObjectSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    post_id: int | None = Field(default=None, alias="id", description="ID записи на стене VK")
    owner_id: int | None = Field(default=None, description="ID владельца стены VK")
    text: str | None = Field(default=None, description="Текст записи на стене VK")
    message: VKCallbackMessageSchema | None = Field(
        default=None,
        description="Сообщение из события VK Callback API",
    )
    user_id: int | None = Field(default=None, description="ID пользователя VK")
    from_id: int | None = Field(default=None, description="ID пользователя VK")
    liker_id: int | None = Field(default=None, description="ID пользователя VK, поставившего лайк")
    first_name: str | None = Field(default=None, description="Имя пользователя VK")
    last_name: str | None = Field(default=None, description="Фамилия пользователя VK")
    copy_history: list[VKCallbackWallPostSchema] = Field(
        default_factory=list,
        description="История копируемых записей для события wall_repost",
    )


class VKCallbackSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    type: str | None = Field(default=None, description="Тип события VK Callback API")
    group_id: int | None = Field(default=None, description="ID сообщества VK")
    event_id: str | None = Field(default=None, description="Уникальный ID события VK Callback API")
    secret: str | None = Field(default=None, description="Секретный ключ VK Callback API")
    api_version: str | None = Field(default=None, alias="v", description="Версия VK Callback API")
    event_object: VKCallbackObjectSchema = Field(
        default_factory=VKCallbackObjectSchema,
        alias="object",
        description="Объект события VK Callback API",
    )

    def is_confirmation(self) -> bool:
        return self.type == VK_CONFIRMATION_EVENT_TYPE

    def is_like(self) -> bool:
        return self.type in VK_LIKE_EVENT_TYPES

    def is_repost(self) -> bool:
        return self.type in VK_REPOST_EVENT_TYPES

    def is_subscription_event(self) -> bool:
        return self.type in VK_SUBSCRIPTION_EVENT_TYPES

    def is_wall_post_new(self) -> bool:
        return self.type in VK_WALL_POST_EVENT_TYPES

    def is_registration_event(self) -> bool:
        return self.type in VK_REGISTRATION_EVENT_TYPES

    def is_expected_group(self, expected_group_id: int) -> bool:
        return self.group_id == expected_group_id

    def has_valid_secret(self, expected_secret: str) -> bool:
        return self.secret == expected_secret

    def get_like_user_id(self) -> int | None:
        return self._normalize_vk_user_id(raw_user_id=self.event_object.liker_id)

    def get_primary_vk_user_id(self) -> int | None:
        if self.is_like():
            return self.get_like_user_id()
        if self.is_repost():
            return self.get_repost_user_id()
        return self.get_vk_user_id()

    def get_repost_user_id(self) -> int | None:
        for raw_user_id in (self.event_object.from_id, self.event_object.owner_id):
            vk_user_id = self._normalize_vk_user_id(raw_user_id=raw_user_id)
            if vk_user_id is not None:
                return vk_user_id
        return None

    def get_repost_external_id(self) -> str | None:
        post = self.get_wall_post()
        return post.external_id if post is not None else None

    def get_reposted_wall_post_external_ids(self) -> tuple[str, ...]:
        external_ids: set[str] = set()
        for copied_post in self.event_object.copy_history:
            post = copied_post.to_wall_post_dto()
            if post is not None:
                external_ids.update(post.external_id_variants)
        return tuple(sorted(external_ids))

    def get_wall_post(self) -> VKWallPostDTO | None:
        if self.event_object.owner_id is None or self.event_object.post_id is None:
            return None

        return VKWallPostDTO(
            owner_id=self.event_object.owner_id,
            post_id=self.event_object.post_id,
        )

    def get_wall_post_text(self) -> str:
        return self.event_object.text or ""

    def get_vk_user_id(self) -> int | None:
        message = self.event_object.message
        raw_user_id: Any = (
            message.from_id
            if message and message.from_id is not None
            else message.user_id
            if message and message.user_id is not None
            else self.event_object.user_id
            if self.event_object.user_id is not None
            else self.event_object.from_id
        )

        return self._normalize_vk_user_id(raw_user_id=raw_user_id)

    def get_first_name(self) -> str | None:
        if self.event_object.first_name:
            return self.event_object.first_name
        if self.event_object.message and self.event_object.message.first_name:
            return self.event_object.message.first_name
        return None

    def get_last_name(self) -> str | None:
        if self.event_object.last_name:
            return self.event_object.last_name
        if self.event_object.message and self.event_object.message.last_name:
            return self.event_object.message.last_name
        return None

    def get_event_object_keys(self) -> tuple[str, ...]:
        return self._get_present_keys(model=self.event_object)

    def get_message_keys(self) -> tuple[str, ...]:
        if self.event_object.message is None:
            return ()
        return self._get_present_keys(model=self.event_object.message)

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
