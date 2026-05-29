from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from application.admin.command.task_promo_code import (
    CreateTaskPromoCodeTaskHandler,
    GetTaskPromoCodeStatsCommand,
    GetTaskPromoCodeStatsHandler,
)
from presentation.http.dto.admin.task_promo_code import (
    CreateTaskPromoCodeTaskRequestSchema,
    CreatedTaskPromoCodeTaskResponseSchema,
    TaskPromoCodeStatsResponseSchema,
)

task_promo_code_admin_router = APIRouter(route_class=DishkaRoute)


@task_promo_code_admin_router.post(
    path="/task-promo-code-tasks",
    name="Создать задание с промокодами",
    response_model=CreatedTaskPromoCodeTaskResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_task_promo_code_task(
    data: CreateTaskPromoCodeTaskRequestSchema,
    handler: FromDishka[CreateTaskPromoCodeTaskHandler],
) -> CreatedTaskPromoCodeTaskResponseSchema:
    result = await handler(data.to_command())
    return CreatedTaskPromoCodeTaskResponseSchema.from_dto(result)


@task_promo_code_admin_router.get(
    path="/task-promo-code-tasks/{tasks_id}/stats",
    name="Получить статистику промокодов задания",
    response_model=TaskPromoCodeStatsResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_task_promo_code_stats(
    tasks_id: int,
    handler: FromDishka[GetTaskPromoCodeStatsHandler],
) -> TaskPromoCodeStatsResponseSchema:
    result = await handler(GetTaskPromoCodeStatsCommand(tasks_id=tasks_id))
    return TaskPromoCodeStatsResponseSchema.from_dto(result)
