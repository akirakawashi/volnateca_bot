from abc import ABC, abstractmethod

from application.admin.dto.task_promo_code import (
    CreateTaskPromoCodeTaskCommand,
    CreatedTaskPromoCodeTaskDTO,
)


class ITaskPromoCodeAdminRepository(ABC):
    @abstractmethod
    async def create_task_with_codes(
        self,
        command: CreateTaskPromoCodeTaskCommand,
    ) -> CreatedTaskPromoCodeTaskDTO:
        raise NotImplementedError
