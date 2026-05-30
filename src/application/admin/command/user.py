from dataclasses import dataclass

from application.admin.command.prize_redemption import to_prize_redemption_admin_dto

ADMIN_USER_LIST_PAGE_SIZE = 50
from application.admin.dto.prize_redemption import PrizeRedemptionAdminDTO
from application.admin.dto.user import (
    UserProfileAdminDTO,
    UserReferralsAdminDTO,
    UserSearchHitDTO,
    UserTaskCompletionAdminDTO,
    UserTransactionAdminDTO,
)
from application.admin.interface.repositories.user import IUserAdminRepository
from application.base_interactor import Interactor
from application.interface.repositories.prize_redemptions import IPrizeRedemptionRepository
from application.interface.repositories.task_completions import ITaskCompletionRepository
from application.interface.repositories.transactions import ITransactionRepository


@dataclass(slots=True, frozen=True, kw_only=True)
class SearchUsersCommand:
    query: str
    limit: int = 20


@dataclass(slots=True, frozen=True, kw_only=True)
class GetUserProfileCommand:
    users_id: int


@dataclass(slots=True, frozen=True, kw_only=True)
class ListUserPrizeRedemptionsCommand:
    users_id: int
    page: int = 1


@dataclass(slots=True, frozen=True, kw_only=True)
class ListUserTaskCompletionsCommand:
    users_id: int
    page: int = 1


@dataclass(slots=True, frozen=True, kw_only=True)
class ListUserTransactionsCommand:
    users_id: int
    page: int = 1


@dataclass(slots=True, frozen=True, kw_only=True)
class GetUserReferralsCommand:
    users_id: int


class SearchUsersHandler(Interactor[SearchUsersCommand, tuple[UserSearchHitDTO, ...]]):
    def __init__(self, user_admin_repository: IUserAdminRepository) -> None:
        self._users = user_admin_repository

    async def __call__(self, command_data: SearchUsersCommand) -> tuple[UserSearchHitDTO, ...]:
        return await self._users.search(
            query=command_data.query,
            limit=max(1, min(command_data.limit, 20)),
        )


class GetUserProfileHandler(Interactor[GetUserProfileCommand, UserProfileAdminDTO | None]):
    def __init__(self, user_admin_repository: IUserAdminRepository) -> None:
        self._users = user_admin_repository

    async def __call__(self, command_data: GetUserProfileCommand) -> UserProfileAdminDTO | None:
        return await self._users.get_profile(users_id=command_data.users_id)


class UserExistsHandler(Interactor[GetUserProfileCommand, bool]):
    def __init__(self, user_admin_repository: IUserAdminRepository) -> None:
        self._users = user_admin_repository

    async def __call__(self, command_data: GetUserProfileCommand) -> bool:
        return await self._users.exists(users_id=command_data.users_id)


class ListUserPrizeRedemptionsHandler(
    Interactor[ListUserPrizeRedemptionsCommand, tuple[PrizeRedemptionAdminDTO, ...]],
):
    def __init__(self, prize_redemption_repository: IPrizeRedemptionRepository) -> None:
        self._prize_redemptions = prize_redemption_repository

    async def __call__(
        self,
        command_data: ListUserPrizeRedemptionsCommand,
    ) -> tuple[PrizeRedemptionAdminDTO, ...]:
        page = max(1, command_data.page)
        offset = (page - 1) * ADMIN_USER_LIST_PAGE_SIZE
        records = await self._prize_redemptions.list_by_user(
            users_id=command_data.users_id,
            limit=ADMIN_USER_LIST_PAGE_SIZE,
            offset=offset,
        )
        return tuple(to_prize_redemption_admin_dto(record) for record in records)


class ListUserTaskCompletionsHandler(
    Interactor[ListUserTaskCompletionsCommand, tuple[UserTaskCompletionAdminDTO, ...]],
):
    def __init__(self, task_completion_repository: ITaskCompletionRepository) -> None:
        self._task_completions = task_completion_repository

    async def __call__(
        self,
        command_data: ListUserTaskCompletionsCommand,
    ) -> tuple[UserTaskCompletionAdminDTO, ...]:
        page = max(1, command_data.page)
        offset = (page - 1) * ADMIN_USER_LIST_PAGE_SIZE
        records = await self._task_completions.list_by_users_id(
            users_id=command_data.users_id,
            limit=ADMIN_USER_LIST_PAGE_SIZE,
            offset=offset,
        )
        return tuple(
            UserTaskCompletionAdminDTO(
                task_completions_id=record.task_completions_id,
                tasks_id=record.tasks_id,
                task_name=record.task_name,
                completion_key=record.completion_key,
                task_completion_status=record.task_completion_status,
                points_awarded=record.points_awarded,
                transactions_id=record.transactions_id,
                rejected_reason=record.rejected_reason,
                checked_at=record.checked_at,
            )
            for record in records
        )


class ListUserTransactionsHandler(
    Interactor[ListUserTransactionsCommand, tuple[UserTransactionAdminDTO, ...]],
):
    def __init__(self, transaction_repository: ITransactionRepository) -> None:
        self._transactions = transaction_repository

    async def __call__(
        self,
        command_data: ListUserTransactionsCommand,
    ) -> tuple[UserTransactionAdminDTO, ...]:
        page = max(1, command_data.page)
        offset = (page - 1) * ADMIN_USER_LIST_PAGE_SIZE
        records = await self._transactions.list_by_users_id(
            users_id=command_data.users_id,
            limit=ADMIN_USER_LIST_PAGE_SIZE,
            offset=offset,
        )
        return tuple(
            UserTransactionAdminDTO(
                transactions_id=record.transactions_id,
                users_id=record.users_id,
                tasks_id=record.tasks_id,
                prizes_id=record.prizes_id,
                transaction_type=record.transaction_type,
                transaction_source=record.transaction_source,
                amount=record.amount,
                balance_before=record.balance_before,
                balance_after=record.balance_after,
                description=record.description,
                created_at=record.created_at,
            )
            for record in records
        )


class GetUserReferralsHandler(Interactor[GetUserReferralsCommand, UserReferralsAdminDTO]):
    def __init__(self, user_admin_repository: IUserAdminRepository) -> None:
        self._users = user_admin_repository

    async def __call__(self, command_data: GetUserReferralsCommand) -> UserReferralsAdminDTO:
        return await self._users.list_referrals_for_user(users_id=command_data.users_id)


__all__ = [
    "ADMIN_USER_LIST_PAGE_SIZE",
    "GetUserProfileCommand",
    "GetUserProfileHandler",
    "GetUserReferralsCommand",
    "GetUserReferralsHandler",
    "ListUserPrizeRedemptionsCommand",
    "ListUserPrizeRedemptionsHandler",
    "ListUserTaskCompletionsCommand",
    "ListUserTaskCompletionsHandler",
    "ListUserTransactionsCommand",
    "ListUserTransactionsHandler",
    "SearchUsersCommand",
    "SearchUsersHandler",
    "UserExistsHandler",
]
