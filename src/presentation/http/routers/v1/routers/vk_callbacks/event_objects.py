from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from presentation.http.dto.request import VKCallbackMessageSchema, VKCallbackWallPostSchema


class VKCallbackEventObjectSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class VKLikeObjectSchema(VKCallbackEventObjectSchema):
    liker_id: int
    object_id: int
    object_owner_id: int
    object_type: Literal["post"]


class VKWallPostObjectSchema(VKCallbackEventObjectSchema):
    post_id: int = Field(alias="id")
    owner_id: int
    text: str | None = None


class VKRepostObjectSchema(VKWallPostObjectSchema):
    from_id: int
    copy_history: list[VKCallbackWallPostSchema] = Field(default_factory=list)


class VKMessageObjectSchema(VKCallbackEventObjectSchema):
    message: VKCallbackMessageSchema


class VKUserObjectSchema(VKCallbackEventObjectSchema):
    user_id: int | None = None
    from_id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
