from dataclasses import dataclass
from enum import Enum

from domain.enums.task import TaskRepeatPolicy


class VKRepostTaskCompletionStatus(str, Enum):
    COMPLETED = "completed"
    ALREADY_COMPLETED = "already_completed"
    REJECTED = "rejected"
    TASK_NOT_FOUND = "task_not_found"
    USER_NOT_REGISTERED = "user_not_registered"
    VK_API_UNAVAILABLE = "vk_api_unavailable"


class VKRepostTaskCreationStatus(str, Enum):
    CREATED = "created"
    ALREADY_EXISTS = "already_exists"
    IGNORED = "ignored"
    INVALID_MARKER = "invalid_marker"
    WRONG_WALL_OWNER = "wrong_wall_owner"


class VKSubscriptionTaskCompletionStatus(str, Enum):
    COMPLETED = "completed"
    ALREADY_COMPLETED = "already_completed"
    REJECTED = "rejected"
    USER_NOT_REGISTERED = "user_not_registered"
    VK_API_UNAVAILABLE = "vk_api_unavailable"


@dataclass(slots=True, frozen=True, kw_only=True)
class VKRepostTaskDTO:
    tasks_id: int
    task_name: str
    external_id: str
    points: int
    repeat_policy: TaskRepeatPolicy
    week_number: int | None


@dataclass(slots=True, frozen=True, kw_only=True)
class VKRepostTaskCompletionDTO:
    status: VKRepostTaskCompletionStatus
    vk_user_id: int
    users_id: int | None = None
    tasks_id: int | None = None
    task_completions_id: int | None = None
    transactions_id: int | None = None
    points_awarded: int = 0
    balance_points: int | None = None
    rejected_reason: str | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class VKRepostTaskCreationDTO:
    status: VKRepostTaskCreationStatus
    event_id: str | None
    tasks_id: int | None = None
    code: str | None = None
    external_id: str | None = None
    points: int | None = None
    week_number: int | None = None
    reason: str | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class VKSubscriptionTaskDTO:
    tasks_id: int
    task_name: str
    external_id: str
    points: int
    repeat_policy: TaskRepeatPolicy
    week_number: int | None


@dataclass(slots=True, frozen=True, kw_only=True)
class VKSubscriptionTaskCompletionDTO:
    status: VKSubscriptionTaskCompletionStatus
    vk_user_id: int
    users_id: int | None = None
    tasks_id: int | None = None
    task_completions_id: int | None = None
    transactions_id: int | None = None
    points_awarded: int = 0
    balance_points: int | None = None
    rejected_reason: str | None = None


class VKPostTasksCreationStatus(str, Enum):
    CREATED = "created"
    ALREADY_EXISTS = "already_exists"
    IGNORED = "ignored"
    INVALID_MARKER = "invalid_marker"
    WRONG_WALL_OWNER = "wrong_wall_owner"


@dataclass(slots=True, frozen=True, kw_only=True)
class VKPostTasksCreationDTO:
    status: VKPostTasksCreationStatus
    event_id: str | None
    external_id: str | None = None
    repost_tasks_id: int | None = None
    like_tasks_id: int | None = None
    repost_points: int | None = None
    like_points: int | None = None
    week_number: int | None = None
    reason: str | None = None


class VKLikeTaskCreationStatus(str, Enum):
    CREATED = "created"
    ALREADY_EXISTS = "already_exists"
    IGNORED = "ignored"
    INVALID_MARKER = "invalid_marker"
    WRONG_WALL_OWNER = "wrong_wall_owner"


class VKLikeTaskCompletionStatus(str, Enum):
    COMPLETED = "completed"
    ALREADY_COMPLETED = "already_completed"
    TASK_NOT_FOUND = "task_not_found"
    USER_NOT_REGISTERED = "user_not_registered"


@dataclass(slots=True, frozen=True, kw_only=True)
class VKLikeTaskDTO:
    tasks_id: int
    task_name: str
    external_id: str
    points: int
    repeat_policy: TaskRepeatPolicy
    week_number: int | None


@dataclass(slots=True, frozen=True, kw_only=True)
class VKLikeTaskCreationDTO:
    status: VKLikeTaskCreationStatus
    event_id: str | None
    tasks_id: int | None = None
    code: str | None = None
    external_id: str | None = None
    points: int | None = None
    week_number: int | None = None
    reason: str | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class VKLikeTaskCompletionDTO:
    status: VKLikeTaskCompletionStatus
    vk_user_id: int
    users_id: int | None = None
    tasks_id: int | None = None
    task_completions_id: int | None = None
    transactions_id: int | None = None
    points_awarded: int = 0
    balance_points: int | None = None
