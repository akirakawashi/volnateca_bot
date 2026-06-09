from dataclasses import dataclass
from datetime import datetime

from application.admin.dto.task_promo_code import (
    CreatedTaskPromoCodeTaskDTO,
    TaskPromoCodeTaskAdminDTO,
)
from application.admin.interface.repositories.task_promo_code import ITaskPromoCodeAdminRepository
from application.base_interactor import Interactor
from application.interface.uow import IUnitOfWork


@dataclass(slots=True, frozen=True, kw_only=True)
class ListTaskPromoCodeTasksCommand:
    pass


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateTaskPromoCodeTaskCommand:
    code: str
    task_name: str
    description: str | None
    points: int
    week_number: int | None
    starts_at: datetime | None
    ends_at: datetime | None
    promo_code: str
    image_attachment: str | None


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateTaskPromoCodeTaskCommand:
    """Частичное обновление текста и картинки партнёрского промокодного задания."""

    tasks_id: int
    fields: frozenset[str]
    description: str | None = None
    image_attachment: str | None = None


class ListTaskPromoCodeTasksHandler(
    Interactor[ListTaskPromoCodeTasksCommand, tuple[TaskPromoCodeTaskAdminDTO, ...]],
):
    def __init__(self, repository: ITaskPromoCodeAdminRepository) -> None:
        self.repository = repository

    async def __call__(
        self,
        command_data: ListTaskPromoCodeTasksCommand,
    ) -> tuple[TaskPromoCodeTaskAdminDTO, ...]:
        del command_data
        return await self.repository.list_tasks()


class CreateTaskPromoCodeTaskHandler(
    Interactor[CreateTaskPromoCodeTaskCommand, CreatedTaskPromoCodeTaskDTO],
):
    def __init__(
        self,
        repository: ITaskPromoCodeAdminRepository,
        uow: IUnitOfWork,
    ) -> None:
        self.repository = repository
        self.uow = uow

    async def __call__(
        self,
        command_data: CreateTaskPromoCodeTaskCommand,
    ) -> CreatedTaskPromoCodeTaskDTO:
        result = await self.repository.create_task_with_code(command=command_data)
        await self.uow.commit()
        return result


class UpdateTaskPromoCodeTaskHandler(
    Interactor[UpdateTaskPromoCodeTaskCommand, TaskPromoCodeTaskAdminDTO | None],
):
    def __init__(
        self,
        repository: ITaskPromoCodeAdminRepository,
        uow: IUnitOfWork,
    ) -> None:
        self.repository = repository
        self.uow = uow

    async def __call__(
        self,
        command_data: UpdateTaskPromoCodeTaskCommand,
    ) -> TaskPromoCodeTaskAdminDTO | None:
        result = await self.repository.update_task(command=command_data)
        if result is None:
            return None
        await self.uow.commit()
        return result


__all__ = [
    "CreateTaskPromoCodeTaskCommand",
    "CreateTaskPromoCodeTaskHandler",
    "ListTaskPromoCodeTasksCommand",
    "ListTaskPromoCodeTasksHandler",
    "UpdateTaskPromoCodeTaskCommand",
    "UpdateTaskPromoCodeTaskHandler",
]
