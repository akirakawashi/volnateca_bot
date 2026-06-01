from abc import ABC, abstractmethod

from application.admin.command.task_promo_code import CreateTaskPromoCodeTaskCommand
from application.admin.dto.task_promo_code import CreatedTaskPromoCodeTaskDTO


class ITaskPromoCodeAdminRepository(ABC):
    @abstractmethod
    async def create_task_with_codes(
        self,
        command: CreateTaskPromoCodeTaskCommand,
    ) -> CreatedTaskPromoCodeTaskDTO:
        raise NotImplementedError
