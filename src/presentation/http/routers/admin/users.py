from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, status

from application.admin.command.user import (
    GetUserProfileHandler,
    GetUserReferralsHandler,
    ListUserPrizeRedemptionsHandler,
    ListUserTaskCompletionsHandler,
    ListUserTransactionsHandler,
    SearchUsersHandler,
    UserExistsHandler,
)
from presentation.http.dto.admin.prize_redemption import PrizeRedemptionsPageResponseSchema
from presentation.http.dto.admin.user import (
    SearchUsersQuerySchema,
    UserListPageQuerySchema,
    UserProfileResponseSchema,
    UserReferralsResponseSchema,
    UserSearchHitResponseSchema,
    UserTaskCompletionsPageResponseSchema,
    UserTransactionsPageResponseSchema,
    get_user_profile_command,
    get_user_referrals_command,
)

users_admin_router = APIRouter(route_class=DishkaRoute)


async def _ensure_user_exists(
    *,
    users_id: int,
    exists_handler: UserExistsHandler,
) -> None:
    if not await exists_handler(get_user_profile_command(users_id=users_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")


@users_admin_router.get(
    path="/users/search",
    name="Поиск пользователей",
    response_model=list[UserSearchHitResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def search_users(
    handler: FromDishka[SearchUsersHandler],
    q: str,
    limit: int = 20,
) -> list[UserSearchHitResponseSchema]:
    result = await handler(SearchUsersQuerySchema(q=q, limit=limit).to_command())
    return [UserSearchHitResponseSchema.from_dto(item) for item in result]


@users_admin_router.get(
    path="/users/{users_id}",
    name="Профиль пользователя",
    response_model=UserProfileResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_user_profile(
    users_id: int,
    handler: FromDishka[GetUserProfileHandler],
) -> UserProfileResponseSchema:
    result = await handler(get_user_profile_command(users_id=users_id))
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return UserProfileResponseSchema.from_dto(result)


@users_admin_router.get(
    path="/users/{users_id}/prize-redemptions",
    name="Заявки на призы пользователя",
    response_model=PrizeRedemptionsPageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def list_user_prize_redemptions(
    users_id: int,
    exists_handler: FromDishka[UserExistsHandler],
    list_handler: FromDishka[ListUserPrizeRedemptionsHandler],
    page: int = 1,
) -> PrizeRedemptionsPageResponseSchema:
    await _ensure_user_exists(users_id=users_id, exists_handler=exists_handler)

    query = UserListPageQuerySchema(page=page)
    result = await list_handler(query.to_redemptions_command(users_id=users_id))
    return PrizeRedemptionsPageResponseSchema.from_page_dto(result)


@users_admin_router.get(
    path="/users/{users_id}/task-completions",
    name="Выполнения заданий пользователя",
    response_model=UserTaskCompletionsPageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def list_user_task_completions(
    users_id: int,
    exists_handler: FromDishka[UserExistsHandler],
    list_handler: FromDishka[ListUserTaskCompletionsHandler],
    page: int = 1,
) -> UserTaskCompletionsPageResponseSchema:
    await _ensure_user_exists(users_id=users_id, exists_handler=exists_handler)

    query = UserListPageQuerySchema(page=page)
    result = await list_handler(query.to_task_completions_command(users_id=users_id))
    return UserTaskCompletionsPageResponseSchema.from_page_dto(result)


@users_admin_router.get(
    path="/users/{users_id}/transactions",
    name="Транзакции пользователя",
    response_model=UserTransactionsPageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def list_user_transactions(
    users_id: int,
    exists_handler: FromDishka[UserExistsHandler],
    list_handler: FromDishka[ListUserTransactionsHandler],
    page: int = 1,
) -> UserTransactionsPageResponseSchema:
    await _ensure_user_exists(users_id=users_id, exists_handler=exists_handler)

    query = UserListPageQuerySchema(page=page)
    result = await list_handler(query.to_transactions_command(users_id=users_id))
    return UserTransactionsPageResponseSchema.from_page_dto(result)


@users_admin_router.get(
    path="/users/{users_id}/referrals",
    name="Рефералы пользователя",
    response_model=UserReferralsResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_user_referrals(
    users_id: int,
    exists_handler: FromDishka[UserExistsHandler],
    handler: FromDishka[GetUserReferralsHandler],
) -> UserReferralsResponseSchema:
    await _ensure_user_exists(users_id=users_id, exists_handler=exists_handler)

    result = await handler(get_user_referrals_command(users_id=users_id))
    return UserReferralsResponseSchema.from_dto(result)
