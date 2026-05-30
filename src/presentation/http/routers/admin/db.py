from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from application.admin.command.truncate_db import TruncateDBCommand, TruncateDBHandler

# TODO DEV: удалить весь файл db.py перед релизом — truncate только для локальной отладки.
db_admin_router = APIRouter(route_class=DishkaRoute)


@db_admin_router.delete(
    path="/db/truncate",
    name="Очистить базу данных",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def truncate_db(
    handler: FromDishka[TruncateDBHandler],
) -> None:
    # TODO DEV: endpoint без runtime-охраны — удалить вместе с db_admin_router перед релизом.
    await handler(TruncateDBCommand())
