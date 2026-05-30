from datetime import date

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, Query, status

from application.admin.command.stats import (
    GetDailyAccrualPointsStatsHandler,
    GetDailyActivityStatsHandler,
    GetDailyNewUsersStatsHandler,
)
from presentation.http.dto.admin.stats import (
    DailyAccrualPointsStatsResponseSchema,
    DailyActivityStatsQuerySchema,
    DailyActivityStatsResponseSchema,
    DailyNewUsersStatsResponseSchema,
)

stats_admin_router = APIRouter(route_class=DishkaRoute)


@stats_admin_router.get(
    path="/stats/daily-activity",
    name="Активность по дням",
    response_model=DailyActivityStatsResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_daily_activity_stats(
    handler: FromDishka[GetDailyActivityStatsHandler],
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    days: int | None = Query(default=None, ge=1, le=90),
) -> DailyActivityStatsResponseSchema:
    query = DailyActivityStatsQuerySchema(from_date=from_date, to_date=to_date, days=days)
    try:
        result = await handler(query.to_activity_command())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return DailyActivityStatsResponseSchema.from_dto(result)


@stats_admin_router.get(
    path="/stats/daily-new-users",
    name="Новые участники по дням",
    response_model=DailyNewUsersStatsResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_daily_new_users_stats(
    handler: FromDishka[GetDailyNewUsersStatsHandler],
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    days: int | None = Query(default=None, ge=1, le=90),
) -> DailyNewUsersStatsResponseSchema:
    query = DailyActivityStatsQuerySchema(from_date=from_date, to_date=to_date, days=days)
    try:
        result = await handler(query.to_new_users_command())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return DailyNewUsersStatsResponseSchema.from_dto(result)


@stats_admin_router.get(
    path="/stats/daily-accrual-points",
    name="Начисления баллов по дням",
    response_model=DailyAccrualPointsStatsResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_daily_accrual_points_stats(
    handler: FromDishka[GetDailyAccrualPointsStatsHandler],
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    days: int | None = Query(default=None, ge=1, le=90),
) -> DailyAccrualPointsStatsResponseSchema:
    query = DailyActivityStatsQuerySchema(from_date=from_date, to_date=to_date, days=days)
    try:
        result = await handler(query.to_accrual_points_command())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return DailyAccrualPointsStatsResponseSchema.from_dto(result)


__all__ = ["stats_admin_router"]
