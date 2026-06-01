from dataclasses import dataclass
from datetime import datetime

from application.admin.dto.task_promo_code import CreatedTaskPromoCodeTaskDTO
from application.admin.interface.repositories.task_promo_code import ITaskPromoCodeAdminRepository
from application.base_interactor import Interactor
from application.interface.uow import IUnitOfWork
from domain.enums.task import TaskRepeatPolicy


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateTaskPromoCodeTaskCommand:
    code: str
    task_name: str
    description: str | None
    points: int
    week_number: int | None
    starts_at: datetime | None
    ends_at: datetime | None
    repeat_policy: TaskRepeatPolicy
    promo_codes: tuple[str, ...]


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
        result = await self.repository.create_task_with_codes(command=command_data)
        await self.uow.commit()
        return result


__all__ = [
    "CreateTaskPromoCodeTaskCommand",
    "CreateTaskPromoCodeTaskHandler",
]
