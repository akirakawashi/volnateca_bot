from pydantic import BaseModel, Field, field_validator

from application.admin.dto.wall_post import PostToWallCommand, PostedToWallDTO
from utils.vk_attachments import extract_vk_attachment


# ── Request ───────────────────────────────────────────────────────────────────


class PostToWallRequestSchema(BaseModel):
    message: str = Field(min_length=1, max_length=16384)
    like_points: int = Field(default=10, gt=0)
    repost_points: int = Field(default=20, gt=0)
    comment_points: int = Field(default=0, ge=0)
    week_number: int | None = Field(default=None, ge=1, le=12)
    attachments: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("attachments", mode="before")
    @classmethod
    def normalize_attachments(cls, value: object) -> object:
        if not isinstance(value, list):
            return value

        normalized: list[object] = []
        for item in value:
            if not isinstance(item, str):
                normalized.append(item)
                continue

            stripped = item.strip()
            if not stripped:
                continue

            normalized.append(extract_vk_attachment(stripped) or stripped)

        return normalized

    def to_command(self) -> PostToWallCommand:
        return PostToWallCommand(
            message=self.message,
            like_points=self.like_points,
            repost_points=self.repost_points,
            comment_points=self.comment_points,
            week_number=self.week_number,
            attachments=tuple(self.attachments) if self.attachments else None,
        )


# ── Response ──────────────────────────────────────────────────────────────────


class PostedToWallResponseSchema(BaseModel):
    post_id: int
    external_id: str
    like_tasks_id: int | None
    repost_tasks_id: int | None
    comment_tasks_id: int | None

    @classmethod
    def from_dto(cls, dto: PostedToWallDTO) -> "PostedToWallResponseSchema":
        return cls(
            post_id=dto.post_id,
            external_id=dto.external_id,
            like_tasks_id=dto.like_tasks_id,
            repost_tasks_id=dto.repost_tasks_id,
            comment_tasks_id=dto.comment_tasks_id,
        )
