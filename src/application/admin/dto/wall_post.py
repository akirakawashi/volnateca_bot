from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class PostToWallCommand:
    message: str
    like_points: int
    repost_points: int
    comment_points: int  # 0 — задание на комментарий не создаётся
    week_number: int | None
    attachments: tuple[str, ...] | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class PostedToWallDTO:
    post_id: int
    external_id: str
    like_tasks_id: int | None
    repost_tasks_id: int | None
    comment_tasks_id: int | None


__all__ = [
    "PostToWallCommand",
    "PostedToWallDTO",
]
