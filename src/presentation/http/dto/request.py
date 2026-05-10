from pydantic import BaseModel, ConfigDict, Field


class VKCallbackMessageSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    from_id: int | None = Field(default=None, description="ID пользователя VK")
    user_id: int | None = Field(default=None, description="ID пользователя VK")
    first_name: str | None = Field(default=None, description="Имя пользователя VK")
    last_name: str | None = Field(default=None, description="Фамилия пользователя VK")
    text: str | None = Field(default=None, description="Текст сообщения пользователя")


class VKCallbackWallPostSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    post_id: int | None = Field(default=None, alias="id", description="ID записи на стене VK")
    owner_id: int | None = Field(default=None, description="ID владельца стены VK")


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
    object_id: int | None = Field(default=None, description="ID объекта, которому поставлен лайк")
    object_owner_id: int | None = Field(default=None, description="ID владельца объекта лайка")
    object_type: str | None = Field(default=None, description="Тип объекта лайка (post, comment, etc.)")
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
