from typing import Any

from pydantic import BaseModel, ConfigDict, Field


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
    first_name: str | None = Field(default=None, description="Имя пользователя VK")
    last_name: str | None = Field(default=None, description="Фамилия пользователя VK")


class VKCallbackSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    type: str | None = Field(default=None, description="Тип события VK Callback API")
    event_object: VKCallbackObjectSchema = Field(
        default_factory=VKCallbackObjectSchema,
        alias="object",
        description="Объект события VK Callback API",
    )

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

        if raw_user_id is None:
            return None

        vk_user_id = int(raw_user_id)
        return vk_user_id if vk_user_id > 0 else None

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
