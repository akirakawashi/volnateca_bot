from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class PostedToWallDTO:
    post_id: int
    external_id: str
    like_tasks_id: int | None
    comment_tasks_id: int | None


__all__ = [
    "PostedToWallDTO",
]
