from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from application.admin.command.task_promo_code import (
    CreateTaskPromoCodeTaskHandler,
    ListTaskPromoCodeTasksCommand,
    ListTaskPromoCodeTasksHandler,
    UpdateTaskPromoCodeTaskHandler,
)
from presentation.http.dto.admin.task_promo_code import (
    CreateTaskPromoCodeTaskRequestSchema,
    CreatedTaskPromoCodeTaskResponseSchema,
    TaskPromoCodeTaskAdminResponseSchema,
    UpdateTaskPromoCodeTaskRequestSchema,
)

task_promo_code_admin_router = APIRouter(route_class=DishkaRoute)


@task_promo_code_admin_router.get(
    path="/task-promo-code-tasks",
    name="Получить список заданий с промокодом",
    response_model=list[TaskPromoCodeTaskAdminResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def list_task_promo_code_tasks(
    handler: FromDishka[ListTaskPromoCodeTasksHandler],
) -> list[TaskPromoCodeTaskAdminResponseSchema]:
    result = await handler(ListTaskPromoCodeTasksCommand())
    return [TaskPromoCodeTaskAdminResponseSchema.from_dto(item) for item in result]


@task_promo_code_admin_router.post(
    path="/task-promo-code-tasks",
    name="Создать задание с промокодом",
    response_model=CreatedTaskPromoCodeTaskResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_task_promo_code_task(
    data: CreateTaskPromoCodeTaskRequestSchema,
    handler: FromDishka[CreateTaskPromoCodeTaskHandler],
) -> CreatedTaskPromoCodeTaskResponseSchema:
    try:
        result = await handler(data.to_command())
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Такой промокод уже используется в другом задании. Укажите уникальный промокод.",
        ) from exc
    return CreatedTaskPromoCodeTaskResponseSchema.from_dto(result)


@task_promo_code_admin_router.patch(
    path="/task-promo-code-tasks/{tasks_id}",
    name="Обновить текст и изображение задания с промокодом",
    response_model=TaskPromoCodeTaskAdminResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_task_promo_code_task(
    tasks_id: int,
    data: UpdateTaskPromoCodeTaskRequestSchema,
    handler: FromDishka[UpdateTaskPromoCodeTaskHandler],
) -> TaskPromoCodeTaskAdminResponseSchema:
    try:
        result = await handler(data.to_command(tasks_id=tasks_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задание с промокодом не найдено")
    return TaskPromoCodeTaskAdminResponseSchema.from_dto(result)
