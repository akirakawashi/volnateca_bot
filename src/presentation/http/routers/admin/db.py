from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from application.admin.command.truncate_db import TruncateDBCommand, TruncateDBHandler

# TODO: удалить db_admin_router (truncate) перед релизом.
# Это служебный dev-only endpoint для локальных сценариев и ручной отладки.
db_admin_router = APIRouter(route_class=DishkaRoute)


@db_admin_router.delete(
    path="/db/truncate",
    name="Очистить базу данных",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def truncate_db(
    handler: FromDishka[TruncateDBHandler],
) -> None:
    # Намеренно без runtime-охраны: endpoint не является продуктовым API и
    # используется только в локальной разработке для dev-сценариев.
    await handler(TruncateDBCommand())
