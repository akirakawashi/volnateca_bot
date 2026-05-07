from typing import Any

from pydantic import BaseModel, ConfigDict, Field

VK_CONFIRMATION_EVENT_TYPE = "confirmation"
VK_LIKE_EVENT_TYPES = frozenset(("like_add", "like_remove"))
VK_REGISTRATION_EVENT_TYPES = frozenset(("message_new", "message_allow"))


class VKCallbackMessageSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    from_id: int | None = Field(default=None, description="ID пользователя VK")
    user_id: int | None = Field(default=None, description="ID пользователя VK")
    first_name: str | None = Field(default=None, description="Имя пользователя VK")
    last_name: str | None = Field(default=None, description="Фамилия пользователя VK")


class VKCallbackObjectSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    message: VKCallbackMessageSchema | None = Field(
        default=None,
        description="Сообщение из события VK Callback API",
    )
    user_id: int | None = Field(default=None, description="ID пользователя VK")
    from_id: int | None = Field(default=None, description="ID пользователя VK")
    liker_id: int | None = Field(default=None, description="ID пользователя VK, поставившего лайк")
    first_name: str | None = Field(default=None, description="Имя пользователя VK")
    last_name: str | None = Field(default=None, description="Фамилия пользователя VK")


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

    def is_registration_event(self) -> bool:
        return self.type in VK_REGISTRATION_EVENT_TYPES

    def is_expected_group(self, expected_group_id: int) -> bool:
        return self.group_id == expected_group_id

    def has_valid_secret(self, expected_secret: str | None) -> bool:
        if not expected_secret:
            return True
        return self.secret == expected_secret

    def get_like_user_id(self) -> int | None:
        return self._normalize_vk_user_id(raw_user_id=self.event_object.liker_id)

    def get_primary_vk_user_id(self) -> int | None:
        if self.is_like():
            return self.get_like_user_id()
        return self.get_vk_user_id()

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
