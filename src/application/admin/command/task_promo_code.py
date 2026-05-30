from application.admin.dto.task_promo_code import (
    CreateTaskPromoCodeTaskCommand,
    CreatedTaskPromoCodeTaskDTO,
)
from application.admin.interface.repositories.task_promo_code import ITaskPromoCodeAdminRepository
from application.base_interactor import Interactor
from application.interface.uow import IUnitOfWork


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
