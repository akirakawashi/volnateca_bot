from dataclasses import dataclass
from datetime import datetime

from domain.enums.prize import PrizeRedemptionStatus
from domain.enums.task import TaskCompletionStatus
from domain.enums.transaction import TransactionSource, TransactionType


@dataclass(slots=True, frozen=True, kw_only=True)
class UserSearchHitDTO:
    users_id: int
    vk_user_id: int
    display_name: str
    vk_screen_name: str | None
    balance_points: int
    current_level: int


@dataclass(slots=True, frozen=True, kw_only=True)
class UserProfileAdminDTO:
    users_id: int
    vk_user_id: int
    first_name: str | None
    last_name: str | None
    vk_screen_name: str | None
    display_name: str
    balance_points: int
    earned_points_total: int
    spent_points_total: int
    current_level: int
    level_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    referrals_sent_count: int
    redemptions_reserved_count: int


@dataclass(slots=True, frozen=True, kw_only=True)
class UserReferralRowDTO:
    referrals_id: int
    users_id: int
    vk_user_id: int
    display_name: str
    vk_screen_name: str | None
    bonus_transactions_id: int | None
    created_at: datetime


@dataclass(slots=True, frozen=True, kw_only=True)
class UserReferralsAdminDTO:
    invited_by: UserReferralRowDTO | None
    invited_users: tuple[UserReferralRowDTO, ...]


@dataclass(slots=True, frozen=True, kw_only=True)
class UserTaskCompletionAdminDTO:
    task_completions_id: int
    tasks_id: int
    task_name: str
    completion_key: str
    task_completion_status: TaskCompletionStatus
    points_awarded: int
    transactions_id: int | None
    rejected_reason: str | None
    checked_at: datetime | None


@dataclass(slots=True, frozen=True, kw_only=True)
class UserTransactionAdminDTO:
    transactions_id: int
    users_id: int
    tasks_id: int | None
    prizes_id: int | None
    transaction_type: TransactionType
    transaction_source: TransactionSource
    amount: int
    balance_before: int
    balance_after: int
    description: str | None
    created_at: datetime


__all__ = [
    "UserProfileAdminDTO",
    "UserReferralRowDTO",
    "UserReferralsAdminDTO",
    "UserSearchHitDTO",
    "UserTaskCompletionAdminDTO",
    "UserTransactionAdminDTO",
]
