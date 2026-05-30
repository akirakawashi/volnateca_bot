from datetime import datetime

from pydantic import BaseModel, Field

from application.admin.command.user import (
    GetUserProfileCommand,
    GetUserReferralsCommand,
    ListUserPrizeRedemptionsCommand,
    ListUserTaskCompletionsCommand,
    ListUserTransactionsCommand,
    SearchUsersCommand,
)
from application.admin.dto.prize_redemption import PrizeRedemptionAdminDTO
from application.admin.dto.user import (
    UserProfileAdminDTO,
    UserReferralRowDTO,
    UserReferralsAdminDTO,
    UserSearchHitDTO,
    UserTaskCompletionAdminDTO,
    UserTransactionAdminDTO,
)
from domain.enums.task import TaskCompletionStatus
from domain.enums.transaction import TransactionSource, TransactionType
from presentation.http.dto.admin.prize_redemption import PrizeRedemptionResponseSchema


class SearchUsersQuerySchema(BaseModel):
    q: str = Field(min_length=1)
    limit: int = Field(default=20, ge=1, le=20)

    def to_command(self) -> SearchUsersCommand:
        return SearchUsersCommand(query=self.q.strip(), limit=self.limit)


class UserSearchHitResponseSchema(BaseModel):
    users_id: int
    vk_user_id: int
    display_name: str
    vk_screen_name: str | None
    balance_points: int
    current_level: int

    @classmethod
    def from_dto(cls, dto: UserSearchHitDTO) -> "UserSearchHitResponseSchema":
        return cls(
            users_id=dto.users_id,
            vk_user_id=dto.vk_user_id,
            display_name=dto.display_name,
            vk_screen_name=dto.vk_screen_name,
            balance_points=dto.balance_points,
            current_level=dto.current_level,
        )


class UserProfileResponseSchema(BaseModel):
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

    @classmethod
    def from_dto(cls, dto: UserProfileAdminDTO) -> "UserProfileResponseSchema":
        return cls(
            users_id=dto.users_id,
            vk_user_id=dto.vk_user_id,
            first_name=dto.first_name,
            last_name=dto.last_name,
            vk_screen_name=dto.vk_screen_name,
            display_name=dto.display_name,
            balance_points=dto.balance_points,
            earned_points_total=dto.earned_points_total,
            spent_points_total=dto.spent_points_total,
            current_level=dto.current_level,
            level_name=dto.level_name,
            is_active=dto.is_active,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            referrals_sent_count=dto.referrals_sent_count,
            redemptions_reserved_count=dto.redemptions_reserved_count,
        )


class UserReferralRowResponseSchema(BaseModel):
    referrals_id: int
    users_id: int
    vk_user_id: int
    display_name: str
    vk_screen_name: str | None
    bonus_transactions_id: int | None
    created_at: datetime

    @classmethod
    def from_dto(cls, dto: UserReferralRowDTO) -> "UserReferralRowResponseSchema":
        return cls(
            referrals_id=dto.referrals_id,
            users_id=dto.users_id,
            vk_user_id=dto.vk_user_id,
            display_name=dto.display_name,
            vk_screen_name=dto.vk_screen_name,
            bonus_transactions_id=dto.bonus_transactions_id,
            created_at=dto.created_at,
        )


class UserReferralsResponseSchema(BaseModel):
    invited_by: UserReferralRowResponseSchema | None
    invited_users: list[UserReferralRowResponseSchema]

    @classmethod
    def from_dto(cls, dto: UserReferralsAdminDTO) -> "UserReferralsResponseSchema":
        return cls(
            invited_by=(
                UserReferralRowResponseSchema.from_dto(dto.invited_by)
                if dto.invited_by is not None
                else None
            ),
            invited_users=[
                UserReferralRowResponseSchema.from_dto(row) for row in dto.invited_users
            ],
        )


class UserTaskCompletionResponseSchema(BaseModel):
    task_completions_id: int
    tasks_id: int
    task_name: str
    completion_key: str
    task_completion_status: TaskCompletionStatus
    points_awarded: int
    transactions_id: int | None
    rejected_reason: str | None
    checked_at: datetime | None

    @classmethod
    def from_dto(cls, dto: UserTaskCompletionAdminDTO) -> "UserTaskCompletionResponseSchema":
        return cls(
            task_completions_id=dto.task_completions_id,
            tasks_id=dto.tasks_id,
            task_name=dto.task_name,
            completion_key=dto.completion_key,
            task_completion_status=dto.task_completion_status,
            points_awarded=dto.points_awarded,
            transactions_id=dto.transactions_id,
            rejected_reason=dto.rejected_reason,
            checked_at=dto.checked_at,
        )


class UserTransactionResponseSchema(BaseModel):
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

    @classmethod
    def from_dto(cls, dto: UserTransactionAdminDTO) -> "UserTransactionResponseSchema":
        return cls(
            transactions_id=dto.transactions_id,
            users_id=dto.users_id,
            tasks_id=dto.tasks_id,
            prizes_id=dto.prizes_id,
            transaction_type=dto.transaction_type,
            transaction_source=dto.transaction_source,
            amount=dto.amount,
            balance_before=dto.balance_before,
            balance_after=dto.balance_after,
            description=dto.description,
            created_at=dto.created_at,
        )


class UserPrizeRedemptionsListSchema(BaseModel):
    items: list[PrizeRedemptionResponseSchema]

    @classmethod
    def from_dtos(cls, dtos: tuple[PrizeRedemptionAdminDTO, ...]) -> "UserPrizeRedemptionsListSchema":
        return cls(items=[PrizeRedemptionResponseSchema.from_dto(dto) for dto in dtos])


class UserListPageQuerySchema(BaseModel):
    page: int = Field(default=1, ge=1)

    def to_redemptions_command(self, *, users_id: int) -> ListUserPrizeRedemptionsCommand:
        return ListUserPrizeRedemptionsCommand(users_id=users_id, page=self.page)

    def to_task_completions_command(self, *, users_id: int) -> ListUserTaskCompletionsCommand:
        return ListUserTaskCompletionsCommand(users_id=users_id, page=self.page)

    def to_transactions_command(self, *, users_id: int) -> ListUserTransactionsCommand:
        return ListUserTransactionsCommand(users_id=users_id, page=self.page)


def get_user_profile_command(*, users_id: int) -> GetUserProfileCommand:
    return GetUserProfileCommand(users_id=users_id)


def get_user_referrals_command(*, users_id: int) -> GetUserReferralsCommand:
    return GetUserReferralsCommand(users_id=users_id)


__all__ = [
    "SearchUsersQuerySchema",
    "UserListPageQuerySchema",
    "UserPrizeRedemptionsListSchema",
    "UserProfileResponseSchema",
    "UserReferralsResponseSchema",
    "UserSearchHitResponseSchema",
    "UserTaskCompletionResponseSchema",
    "UserTransactionResponseSchema",
    "get_user_profile_command",
    "get_user_referrals_command",
]
