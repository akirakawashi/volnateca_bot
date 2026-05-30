from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from application.admin.command.task_promo_code import CreateTaskPromoCodeTaskHandler
from presentation.http.dto.admin.task_promo_code import (
    CreateTaskPromoCodeTaskRequestSchema,
    CreatedTaskPromoCodeTaskResponseSchema,
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
