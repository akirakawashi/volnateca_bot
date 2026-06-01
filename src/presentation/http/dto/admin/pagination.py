from pydantic import BaseModel, Field


class AdminListPageResponseSchema(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    has_more: bool


__all__ = ["AdminListPageResponseSchema"]
