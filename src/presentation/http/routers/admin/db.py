from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, status

from application.admin.command.truncate_db import TruncateDBCommand, TruncateDBHandler
from settings.app.app import AppSettings

db_admin_router = APIRouter(route_class=DishkaRoute)


@db_admin_router.delete(
    path="/db/truncate",
    name="Очистить базу данных",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def truncate_db(
    handler: FromDishka[TruncateDBHandler],
    app_settings: FromDishka[AppSettings],
) -> None:
    if not app_settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступно только в DEBUG-режиме",
        )
    await handler(TruncateDBCommand())
